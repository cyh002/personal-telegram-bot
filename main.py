#!/usr/bin/env python
import os
import logging
from dotenv import load_dotenv

from src.llm.base import LLMProvider
from src.prompt import PromptManager
from src.bot import TelegramBot

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

def main():
    """Main function to run the bot"""
    # Get configuration from environment variables
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    provider_type = os.getenv("LLM_PROVIDER", "local")  # Default to local if not specified
    
    # Get provider-specific configuration
    api_key = os.getenv(f"{provider_type.upper()}_API_KEY")
    model_name = os.getenv(f"{provider_type.upper()}_MODEL_NAME")
    
    # Additional provider-specific configuration
    kwargs = {}
    if provider_type.lower() == "local":
        kwargs["base_url"] = os.getenv("LOCAL_BASE_URL", "http://localhost:8000/v1")
    
    # Create LLM provider
    try:
        llm_provider = LLMProvider.create_provider(
            provider_type=provider_type,
            api_key=api_key,
            model_name=model_name,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to create LLM provider: {e}")
        return
    
    # Create prompt manager
    prompt_manager = PromptManager()
    
    # Create and run the bot
    bot = TelegramBot(telegram_token, llm_provider, prompt_manager)
    logger.info(f"Bot started with provider: {provider_type}, model: {model_name}")
    bot.run()

if __name__ == "__main__":
    main()