"""
LLM API Clients for Benchmark Pipeline
"""

import os
import time
import json
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)

class BaseLLMClient(ABC):
    """Base class for LLM clients."""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
    
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response from LLM."""
        pass

class OpenAIClient(BaseLLMClient):
    """OpenAI API Client."""
    
    def __init__(self, api_key: str, model_name: str = "gpt-3.5-turbo"):
        super().__init__(api_key, model_name)
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0
            )
            
            end_time = time.time()
            
            # Safely handle response content
            response_content = response.choices[0].message.content
            if response_content is None:
                response_content = ""
            
            return {
                "response": response_content.strip(),
                "model": self.model_name,
                "provider": "openai",
                "response_time": end_time - start_time,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "success": True,
                "error": None
            }
        except Exception as e:
            end_time = time.time()
            logger.error(f"OpenAI API error: {e}")
            return {
                "response": None,
                "model": self.model_name,
                "provider": "openai", 
                "response_time": end_time - start_time,
                "tokens_used": None,
                "success": False,
                "error": str(e)
            }

class GoogleClient(BaseLLMClient):
    """Google Gemini API Client."""
    
    def __init__(self, api_key: str, model_name: str = "gemini-1.5-flash"):
        super().__init__(api_key, model_name)
        try:
            import google.generativeai as genai  # type: ignore
            genai.configure(api_key=api_key)  # type: ignore
            self.model = genai.GenerativeModel(model_name)  # type: ignore
        except ImportError:
            raise ImportError("Please install google-generativeai: pip install google-generativeai")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using Google Gemini API."""
        start_time = time.time()
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "max_output_tokens": max_tokens,
                    "temperature": 0
                }
            )
            
            end_time = time.time()
            
            return {
                "response": response.text.strip() if response.text else None,
                "model": self.model_name,
                "provider": "google",
                "response_time": end_time - start_time,
                "tokens_used": None,  # Google doesn't provide token count in response
                "success": True,
                "error": None
            }
        except Exception as e:
            end_time = time.time()
            logger.error(f"Google API error: {e}")
            return {
                "response": None,
                "model": self.model_name,
                "provider": "google",
                "response_time": end_time - start_time,
                "tokens_used": None,
                "success": False,
                "error": str(e)
            }

class DeepSeekClient(BaseLLMClient):
    """DeepSeek API Client."""
    
    def __init__(self, api_key: str, model_name: str = "deepseek-chat"):
        super().__init__(api_key, model_name)
        try:
            from openai import OpenAI
            # DeepSeek uses OpenAI-compatible API
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com"
            )
        except ImportError:
            raise ImportError("Please install openai: pip install openai")
    
    def generate(self, prompt: str, max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate response using DeepSeek API."""
        start_time = time.time()
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0
            )
            
            end_time = time.time()
            
            # Safely handle response content
            response_content = response.choices[0].message.content
            if response_content is None:
                response_content = ""
            
            return {
                "response": response_content.strip(),
                "model": self.model_name,
                "provider": "deepseek",
                "response_time": end_time - start_time,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "success": True,
                "error": None
            }
        except Exception as e:
            end_time = time.time()
            logger.error(f"DeepSeek API error: {e}")
            return {
                "response": None,
                "model": self.model_name,
                "provider": "deepseek",
                "response_time": end_time - start_time,
                "tokens_used": None,
                "success": False,
                "error": str(e)
            }

def create_llm_client(provider: str, api_key: str, model_name: Optional[str] = None) -> BaseLLMClient:
    """Factory function to create LLM clients."""
    
    if provider.lower() == "openai":
        model_name = model_name or "gpt-3.5-turbo"
        return OpenAIClient(api_key, model_name)
    elif provider.lower() == "google":
        model_name = model_name or "gemini-1.5-flash"
        return GoogleClient(api_key, model_name)
    elif provider.lower() == "deepseek":
        model_name = model_name or "deepseek-chat"
        return DeepSeekClient(api_key, model_name)
    else:
        raise ValueError(f"Unsupported provider: {provider}") 