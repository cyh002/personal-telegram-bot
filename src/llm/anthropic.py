from typing import List, Dict, Any, Optional
import anthropic
from src.llm.base import LLMProvider

class AnthropicProvider(LLMProvider):
    """Anthropic API provider"""
    
    def __init__(self, api_key: str, model_name: str, **kwargs):
        """Initialize the Anthropic provider"""
        self.api_key = api_key
        self.model_name = model_name
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_response(self, messages: List[Dict[str, str]], temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Generate a response using Anthropic API"""
        # Convert messages to Anthropic format
        converted_messages = []
        for msg in messages:
            role = "assistant" if msg["role"] == "assistant" else "user" if msg["role"] == "user" else "system"
            converted_messages.append({"role": role, "content": msg["content"]})
        
        response = self.client.messages.create(
            model=self.model_name,
            messages=converted_messages,
            temperature=temperature,
            max_tokens=max_tokens if max_tokens else 1024
        )
        return response.content[0].text