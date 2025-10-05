#!/usr/bin/env python3
import logging
from telegram.ext import Application, CommandHandler
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update, context):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    logger.info(f"User {chat_id} started the bot")
    
    await update.message.reply_text(
        "🤖 *TradePods Trading Bot Started!*\n\n"
        "This bot receives trading signals from TradingView and forwards them to you.\n\n"
        "📋 *Available Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show help message\n" 
        "/status - Check bot status\n\n"
        f"🆔 *Your Chat ID:* `{chat_id}`\n"
        "_(Add this to ALLOWED_CHAT_IDS in .env)_",
        parse_mode='Markdown'
    )

async def help_command(update, context):
    """Handle /help command"""
    help_text = """
🔧 *Available Commands:*
/start - Start the bot
/help - Show this help message  
/status - Check bot status

📊 *About This Bot:*
This bot receives trading signals from TradingView webhooks and forwards them to authorized users.

🔧 *Setup:*
1. Add your Chat ID to ALLOWED_CHAT_IDS in .env
2. Configure TradingView webhook with your server URL
3. Set allowed tokens and strategies in .env

📝 *Support:* Contact bot admin for assistance
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status_command(update, context):
    """Handle /status command"""
    chat_id = update.effective_chat.id
    is_authorized = chat_id in Config.ALLOWED_CHAT_IDS if Config.ALLOWED_CHAT_IDS else True
    
    status_text = f"""
📊 *Bot Status Report*

🆔 *Your Chat ID:* `{chat_id}`
🔒 *Authorization:* {'✅ Authorized' if is_authorized else '❌ Not Authorized'}
🪙 *Allowed Tokens:* {len(Config.ALLOWED_TOKENS)} configured
📈 *Allowed Strategies:* {len(Config.ALLOWED_STRATEGIES)} configured

💡 *Tip:* Add your Chat ID to ALLOWED_CHAT_IDS in .env to receive signals
    """
    await update.message.reply_text(status_text, parse_mode='Markdown')

def main():
    """Start the bot"""
    logger.info("Starting TradePods Trading Bot...")
    
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in .env file")
        return
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Start the bot
    logger.info("Bot is starting with polling...")
    logger.info("Press Ctrl+C to stop the bot")
    
    try:
        application.run_polling(allowed_updates=['message'])
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")

if __name__ == '__main__':
    main()