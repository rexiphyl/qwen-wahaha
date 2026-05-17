"""OpenRouter LLM client for text-to-SQL generation."""
import requests
import json
import time
from typing import Optional, Dict, Any
from loguru import logger
from src.core.config import Config


class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.MODEL_NAME
        self.base_url = Config.OPENROUTER_BASE_URL
        self.temperature = Config.TEMPERATURE
        self.max_tokens = Config.MAX_TOKENS
        
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")
    
    def generate_response(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate a response from the LLM.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Override default temperature
            max_tokens: Override default max tokens
            
        Returns:
            Dictionary containing response and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Text-to-SQL Agent"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens
        }
        
        start_time = time.time()
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract usage metrics
            usage = result.get("usage", {})
            
            return {
                "success": True,
                "content": content,
                "input_tokens": usage.get("prompt_tokens", 0),
                "output_tokens": usage.get("completion_tokens", 0),
                "total_tokens": usage.get("total_tokens", 0),
                "model": result.get("model", self.model),
                "latency_ms": int((time.time() - start_time) * 1000),
                "raw_response": result
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return {
                "success": False,
                "error": str(e),
                "input_tokens": 0,
                "output_tokens": 0,
                "total_tokens": 0,
                "latency_ms": int((time.time() - start_time) * 1000)
            }
    
    def generate_sql(self, question: str, schema_context: str) -> Dict[str, Any]:
        """Generate SQL from a natural language question.
        
        Args:
            question: Natural language question
            schema_context: Database schema context
            
        Returns:
            Dictionary with SQL and metadata
        """
        system_prompt = f"""You are an expert SQL generator. Given a database schema and a natural language question, generate ONLY the SQL query that answers the question.

Rules:
1. Output ONLY the SQL query, no explanations
2. Use proper SQLite syntax
3. Use table aliases for readability
4. Include necessary JOINs when querying related tables
5. Handle date/time functions appropriately for SQLite
6. If the question is about vegetarian/vegan food, focus on menu_items.is_vegetarian or menu_items.is_vegan columns joined with order_items and restaurant_orders

Database Schema:
{schema_context}

Always analyze the question carefully to identify the correct tables based on keywords:
- vegetarian, vegan, food → menu_items, order_items, restaurant_orders
- booking, reservation → hotel_bookings
- rental, car, vehicle → car_rentals, cars
- payment → payments
- review, rating → reviews
- customer → customers
"""

        result = self.generate_response(
            prompt=f"Question: {question}\n\nGenerate SQL:",
            system_prompt=system_prompt
        )
        
        if result["success"]:
            # Clean up the response to extract just SQL
            sql = result["content"].strip()
            # Remove markdown code blocks if present
            if sql.startswith("```sql"):
                sql = sql[6:]
            if sql.startswith("```"):
                sql = sql[3:]
            if sql.endswith("```"):
                sql = sql[:-3]
            sql = sql.strip()
            result["sql"] = sql
        else:
            result["sql"] = ""
            
        return result
