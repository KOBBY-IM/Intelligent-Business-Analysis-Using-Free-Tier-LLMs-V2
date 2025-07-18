"""
llm_clients.py
API clients for Groq, Google Gemini, and OpenRouter (free-tier LLMs).
"""
from typing import Optional, Dict
import streamlit as st
import requests
import os

def get_secret_or_env(key: str, env_key: str) -> str:
    # Try Streamlit secrets, then environment variable
    try:
        value = st.secrets["api_keys"].get(key)
        if value:
            return value
    except Exception:
        pass
    return os.environ.get(env_key)

class GroqClient:
    """
    Client for Groq LLM API (llama3-70b-8192).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3-70b-8192"):
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
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7)
        }
        try:
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Groq API error: {e}")

class GeminiClient:
    """
    Client for Google Gemini LLM API (gemini-1.5-pro).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-pro"):
        self.api_key = api_key or get_secret_or_env("google_gemini_api_key", "GOOGLE_GEMINI_API_KEY")
        self.model = model
        self.endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"

    def generate(self, prompt: str, **kwargs) -> str:
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": kwargs.get("temperature", 0.7),
                "maxOutputTokens": kwargs.get("max_tokens", 512)
            }
        }
        try:
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            raise RuntimeError(f"Gemini API error: {e}")

class OpenRouterClient:
    """
    Client for OpenRouter LLM API (supports multiple models).
    """
    def __init__(self, api_key: Optional[str] = None, model: str = "mistralai/mistral-small-3.2-24b-instruct"):
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
            "max_tokens": kwargs.get("max_tokens", 512),
            "temperature": kwargs.get("temperature", 0.7)
        }
        try:
            resp = requests.post(self.endpoint, headers=headers, json=data, timeout=30)
            resp.raise_for_status()
            result = resp.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"OpenRouter API error: {e}")

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