import logging
from typing import Dict, List, Any, Optional
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

from src.llm.base import LLMProvider
from src.prompt import PromptManager

class TelegramBot:
    """Telegram bot for interacting with LLM providers"""
    
    def __init__(self, telegram_token: str, llm_provider: LLMProvider, prompt_manager: PromptManager = None):
        """Initialize the Telegram bot with token and LLM provider"""
        self.telegram_token = telegram_token
        self.llm_provider = llm_provider
        self.prompt_manager = prompt_manager or PromptManager()
        
        # Set up logging
        self.logger = logging.getLogger(__name__)
        
        # Create the application
        self.application = Application.builder().token(telegram_token).build()
        
        # Register handlers
        self._register_handlers()
    
    def _register_handlers(self):
        """Register command and message handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("clear", self.clear_history))
        self.application.add_handler(CommandHandler("prompt", self.set_prompt))
        self.application.add_handler(CommandHandler("prompts", self.list_prompts))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.bot_reply))
    
    def run(self):
        """Run the bot"""
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
    
    @staticmethod
    def manage_conversation_history(messages: List[Dict[str, str]], max_messages: int = 10) -> List[Dict[str, str]]:
        """Keep conversation history at a reasonable length"""
        # Always keep the system message
        system_message = messages[0]
        messages = messages[1:]  # Remove system message temporarily
        
        # If we have too many messages, remove oldest ones (keeping the pairs)
        if len(messages) > max_messages * 2:
            # Remove oldest user-assistant message pairs
            messages = messages[-(max_messages * 2):]
        
        # Add system message back at the beginning
        return [system_message] + messages
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /start is issued"""
        user = update.effective_user
        # Initialize chat history for this user with default prompt
        default_prompt = self.prompt_manager.get_prompt("default") or "You are a helpful assistant. Keep replies within 20 words."
        context.user_data["messages"] = [{'role': 'system', 'content': default_prompt}]
        
        await update.message.reply_html(
            rf"Hi {user.mention_html()}! I'm ready to chat. Use /help to see available commands.",
            reply_markup=ForceReply(selective=True),
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued"""
        help_text = (
            "Available commands:\n"
            "/start - Start or restart the bot\n"
            "/help - Show this help message\n"
            "/clear - Clear conversation history\n"
            "/prompt [name] - Use a saved prompt as system message\n"
            "/prompts - List available prompts"
        )
        await update.message.reply_text(help_text)
    
    async def clear_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Clear the conversation history"""
        default_prompt = self.prompt_manager.get_prompt("default") or "You are a helpful assistant. Keep replies within 20 words."
        context.user_data["messages"] = [{'role': 'system', 'content': default_prompt}]
        await update.message.reply_text("Conversation history has been cleared.")
    
    async def set_prompt(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Set the system prompt from a prompt file"""
        args = context.args
        if not args:
            await update.message.reply_text("Please provide a prompt name. Use /prompts to see available prompts.")
            return
        
        prompt_name = args[0]
        prompt_content = self.prompt_manager.get_prompt(prompt_name)
        
        if not prompt_content:
            await update.message.reply_text(f"Prompt '{prompt_name}' not found. Use /prompts to see available prompts.")
            return
        
        # Initialize messages if not present
        if "messages" not in context.user_data:
            context.user_data["messages"] = []
        
        # Replace system message or add if not present
        if context.user_data["messages"] and context.user_data["messages"][0]["role"] == "system":
            context.user_data["messages"][0] = {"role": "system", "content": prompt_content}
        else:
            context.user_data["messages"] = [{"role": "system", "content": prompt_content}] + context.user_data["messages"]
        
        await update.message.reply_text(f"System prompt set to '{prompt_name}'.")
    
    async def list_prompts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """List available prompts"""
        prompts = self.prompt_manager.list_prompts()
        if not prompts:
            await update.message.reply_text("No prompts available. Add prompt files to the 'prompts' directory.")
            return
        
        prompt_list = "\n".join([f"- {name}" for name in prompts.keys()])
        await update.message.reply_text(f"Available prompts:\n{prompt_list}")
    
    async def bot_reply(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process user message and generate a response"""
        user = update.message.from_user
        
        self.logger.info("Question from User %s: %s", user.first_name, update.message.text)
        
        # Initialize messages if not present
        if "messages" not in context.user_data:
            default_prompt = self.prompt_manager.get_prompt("default") or "You are a helpful assistant. Keep replies within 20 words."
            context.user_data["messages"] = [{'role': 'system', 'content': default_prompt}]
        
        if update.message.text != '':
            user_input = update.message.text
            
            # Add user message to history
            context.user_data["messages"].append({'role': 'user', 'content': user_input})
            
            # Manage history length before sending to API
            context.user_data["messages"] = self.manage_conversation_history(context.user_data["messages"])
            
            try:
                # Generate response using the LLM provider
                llm_reply = self.llm_provider.generate_response(
                    messages=context.user_data["messages"],
                    temperature=0.7
                )
                
                # Add assistant response to history
                context.user_data["messages"].append({'role': 'assistant', 'content': llm_reply})
                
                await update.message.reply_text(llm_reply)
            except Exception as e:
                self.logger.error("Error generating response: %s", e)
                await update.message.reply_text(f"Sorry, I encountered an error: {str(e)}")