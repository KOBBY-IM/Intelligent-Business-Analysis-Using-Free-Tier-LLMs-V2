"""
llm_clients.py
API clients for Groq, Google Gemini, and OpenRouter (free-tier LLMs).
"""
from typing import Optional, Dict
import streamlit as st
import requests
import os
import time
import random

def get_secret_or_env(key: str, env_key: str) -> str:
    # Try Streamlit secrets, then environment variable
    try:
        value = st.secrets["api_keys"].get(key)
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(env_key)

class BaseLLMClient:
    """Base class with common retry logic and error handling."""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def _retry_with_backoff(self, func, *args, **kwargs):
        """Retry function with exponential backoff."""
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:  # Rate limit
                    delay = self.base_delay * (2 ** attempt) + random.uniform(0, 1)
                    print(f"Rate limited, waiting {delay:.2f}s before retry {attempt + 1}")
                    time.sleep(delay)
                    continue
                elif e.response.status_code >= 500:  # Server error
                    delay = self.base_delay * (2 ** attempt)
                    print(f"Server error, waiting {delay:.2f}s before retry {attempt + 1}")
                    time.sleep(delay)
                    continue
                else:
                    raise
            except (requests.exceptions.RequestException, Exception) as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                print(f"Request failed, waiting {delay:.2f}s before retry {attempt + 1}: {e}")
                time.sleep(delay)
        
        raise RuntimeError(f"Failed after {self.max_retries} retries")

class GroqClient(BaseLLMClient):
    """
    Client for Groq LLM API (llama3-70b-8192).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3-70b-8192", max_retries: int = 3):
        super().__init__(max_retries=max_retries)
        self.api_key = api_key or get_secret_or_env("groq_api_key", "GROQ_API_KEY")
        self.model = model
        self.endpoint = "https://api.groq.com/openai/v1/chat/completions"

    def generate(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1024),  # Increased for better responses
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        def _make_request():
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            
            # Safely access nested response structure
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid API response: missing choices")
            choice = result["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError("Invalid API response: missing message content")
            
            return choice["message"]["content"].strip()
        
        return self._retry_with_backoff(_make_request)

class GeminiClient(BaseLLMClient):
    """
    Client for Google Gemini LLM API (gemini-1.5-pro).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro", max_retries: int = 3):
        super().__init__(max_retries=max_retries)
        self.api_key = api_key or get_secret_or_env("google_gemini_api_key", "GOOGLE_GEMINI_API_KEY")
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate(self, prompt: str, **kwargs) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 1024)  # Increased for better responses
            }
        }
        
        def _make_request():
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            
            # Safely access nested response structure
            if "candidates" not in result or not result["candidates"]:
                raise ValueError("Invalid API response: missing candidates")
            candidate = result["candidates"][0]
            if "content" not in candidate or "parts" not in candidate["content"] or not candidate["content"]["parts"]:
                raise ValueError("Invalid API response: missing content parts")
            if "text" not in candidate["content"]["parts"][0]:
                raise ValueError("Invalid API response: missing text content")
            
            return candidate["content"]["parts"][0]["text"].strip()
        
        return self._retry_with_backoff(_make_request)

class OpenRouterClient(BaseLLMClient):
    """
    Client for OpenRouter LLM API (supports multiple models).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "mistralai/mistral-7b-instruct", max_retries: int = 5):
        super().__init__(max_retries=max_retries, base_delay=2.0)  # More retries and longer delays for OpenRouter
        self.api_key = api_key or get_secret_or_env("openrouter_api_key", "OPENROUTER_API_KEY")
        self.model = model
        self.endpoint = "https://openrouter.ai/api/v1/chat/completions"

    def generate(self, prompt: str, **kwargs) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.environ.get("OPENROUTER_REFERER", "https://your-app-url.com"),
            "X-Title": os.environ.get("OPENROUTER_TITLE", "BusinessAnalysisRAG")
        }
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": kwargs.get("max_tokens", 1024),  # Increased for better responses
            "temperature": kwargs.get("temperature", 0.7)
        }
        
        def _make_request():
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            result = resp.json()
            
            # Safely access nested response structure
            if "choices" not in result or not result["choices"]:
                raise ValueError("Invalid API response: missing choices")
            choice = result["choices"][0]
            if "message" not in choice or "content" not in choice["message"]:
                raise ValueError("Invalid API response: missing message content")
            
            return choice["message"]["content"].strip()
        
        try:
            return self._retry_with_backoff(_make_request)
        except Exception as e:
            # If all retries fail, provide a fallback response
            print(f"OpenRouter failed after all retries: {e}")
            # Don't expose detailed error information that might contain sensitive data
            return "Unable to generate response due to API limitations. Please try again later or contact support."

# Utility function to select and instantiate a client by provider/model

def get_llm_client(provider: str, model: str = None) -> object:
    """
    Factory to get the correct LLM client for a provider.
    Args:
        provider: 'groq', 'gemini', or 'openrouter'
        model: Optional model name
    Returns:
        LLM client instance
    """
    if provider == "groq":
        return GroqClient(model=model) if model else GroqClient()
    elif provider == "gemini":
        return GeminiClient(model=model) if model else GeminiClient()
    elif provider == "openrouter":
        return OpenRouterClient(model=model) if model else OpenRouterClient()
    else:
        raise ValueError(f"Unknown LLM provider: {provider}") 