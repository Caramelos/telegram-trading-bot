import asyncio
from telegram.ext import Application
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_bot():
    """Simple test to verify bot token works"""
    try:
        application = Application.builder().token(Config.BOT_TOKEN).build()
        async with application:
            await application.initialize()
            me = await application.bot.get_me()
            logger.info(f"✅ Bot connected successfully: @{me.username}")
            logger.info(f"Bot name: {me.first_name}")
            logger.info(f"Bot ID: {me.id}")
            
    except Exception as e:
        logger.error(f"❌ Bot connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_bot())