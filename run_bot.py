import asyncio
from telegram_bot import TelegramBot
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the Telegram bot"""
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    logger.info("Starting Telegram Trading Bot...")
    telegram_bot = TelegramBot()
    
    try:
        await telegram_bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")

if __name__ == "__main__":
    asyncio.run(main())