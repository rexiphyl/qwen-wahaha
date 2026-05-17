"""
LLM Client for OpenRouter - Professional Implementation
"""
import requests
import json
from typing import Dict, Any, Optional
from loguru import logger
from src.core.config import Config, LLMResponse

class LLMClient:
    """Professional LLM client for OpenRouter API"""
    
    def __init__(self):
        self.api_key = Config.OPENROUTER_API_KEY
        self.model = Config.MODEL_NAME
        self.url = Config.OPENROUTER_URL
        
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not found in environment variables")
        
        logger.info(f"LLM Client initialized with model: {self.model}")
    
    def chat(self, system_prompt: str, user_message: str, response_format: Optional[str] = None) -> LLMResponse:
        """Send chat request to LLM and get structured response"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",
            "X-Title": "Text-to-SQL Multi-Agent System"
        }
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.1,
            "max_tokens": 2000
        }
        
        if response_format == "json":
            payload["response_format"] = {"type": "json_object"}
        
        try:
            logger.debug(f"Sending request to LLM: {user_message[:100]}...")
            response = requests.post(self.url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse confidence from response or default
            confidence = 0.8
            reasoning = "Analysis completed successfully"
            
            # Try to extract structured data if JSON requested
            if response_format == "json":
                try:
                    parsed = json.loads(content)
                    confidence = parsed.get("confidence", 0.8)
                    reasoning = parsed.get("reasoning", "JSON analysis completed")
                except json.JSONDecodeError:
                    logger.warning("Failed to parse JSON response, using defaults")
            
            logger.info(f"LLM response received (confidence: {confidence})")
            
            return LLMResponse(
                content=content,
                confidence=confidence,
                reasoning=reasoning,
                metadata={"model": self.model, "usage": result.get("usage", {})}
            )
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM API request failed: {str(e)}")
            return LLMResponse(
                content="",
                confidence=0.0,
                reasoning=f"API Error: {str(e)}",
                metadata={"error": str(e)}
            )
        except Exception as e:
            logger.error(f"Unexpected error in LLM client: {str(e)}")
            return LLMResponse(
                content="",
                confidence=0.0,
                reasoning=f"Unexpected Error: {str(e)}",
                metadata={"error": str(e)}
            )
