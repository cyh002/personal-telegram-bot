from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.llm.base import LLMProvider

class OpenRouterProvider(LLMProvider):
    """OpenRouter API provider"""
    
    def __init__(self, api_key: str, model_name: str, **kwargs):
        """Initialize the OpenRouter provider"""
        self.api_key = api_key
        self.model_name = model_name
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Generate a response using OpenRouter API"""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content