"""
LLM Client for OpenRouter API
Supports NVIDIA Nemotron-3 Super 120B model
"""

import os
import json
import requests
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class OpenRouterClient:
    """Client for OpenRouter API with NVIDIA Nemotron model"""
    
    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        self.model_name = model_name or os.getenv("MODEL_NAME", "nvidia/nemotron-3-super-120b-a12b:free")
        self.base_url = "https://openrouter.ai/api/v1"
        
        if not self.api_key:
            raise ValueError(
                "OPENROUTER_API_KEY not found. Please set it in your .env file or environment variables."
            )
    
    def generate_completion(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate completion using OpenRouter API
        
        Args:
            prompt: User prompt
            system_prompt: Optional system instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dictionary with completion text and metadata
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:8501",  # For Streamlit app
            "X-Title": "Business Intelligence Agent"
        }
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            
            return {
                "success": True,
                "content": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": result.get("model", self.model_name)
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "content": None
            }
        except (KeyError, IndexError) as e:
            return {
                "success": False,
                "error": f"Invalid response format: {str(e)}",
                "content": None
            }
    
    def generate_structured_output(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        output_schema: Optional[Dict] = None,
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output
        
        Args:
            prompt: User prompt
            system_prompt: System instruction
            output_schema: Expected output schema (optional)
            temperature: Lower temperature for more deterministic output
            
        Returns:
            Parsed JSON response
        """
        if system_prompt is None:
            system_prompt = "You are a helpful assistant that outputs valid JSON."
        else:
            system_prompt += " Always respond with valid JSON only, no markdown formatting."
        
        result = self.generate_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=2048
        )
        
        if not result["success"]:
            return result
        
        # Try to parse JSON from response
        content = result["content"].strip()
        
        # Remove markdown code blocks if present
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        try:
            parsed_json = json.loads(content)
            result["parsed"] = parsed_json
            return result
        except json.JSONDecodeError as e:
            result["success"] = False
            result["error"] = f"JSON parsing failed: {str(e)}"
            result["raw_content"] = content
            return result


# Example usage
if __name__ == "__main__":
    client = OpenRouterClient()
    
    # Test basic completion
    response = client.generate_completion(
        prompt="What is 2+2?",
        system_prompt="You are a helpful math assistant."
    )
    
    if response["success"]:
        print(f"Response: {response['content']}")
        print(f"Model: {response['model']}")
        print(f"Usage: {response['usage']}")
    else:
        print(f"Error: {response['error']}")
