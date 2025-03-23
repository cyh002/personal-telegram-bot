from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def __init__(self, api_key: str, model_name: str, **kwargs):
        """Initialize the LLM provider with api key and model name"""
        pass
    
    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Generate a response from the LLM provider based on a list of messages"""
        pass
    
    @staticmethod
    def create_provider(provider_type: str, api_key: str, model_name: str, **kwargs) -> 'LLMProvider':
        """Factory method to create the appropriate provider"""
        if provider_type.lower() == "openai":
            from src.llm.openai import OpenAIProvider
            return OpenAIProvider(api_key, model_name, **kwargs)
        elif provider_type.lower() == "anthropic":
            from src.llm.anthropic import AnthropicProvider
            return AnthropicProvider(api_key, model_name, **kwargs)
        elif provider_type.lower() == "openrouter":
            from src.llm.openrouter import OpenRouterProvider
            return OpenRouterProvider(api_key, model_name, **kwargs)
        elif provider_type.lower() == "local":
            from src.llm.local import LocalProvider
            return LocalProvider(api_key, model_name, **kwargs)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")