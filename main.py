import asyncio
import threading
import time
from flask import Flask
from telegram_bot import TelegramBot
from webhook_server import app
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingBot:
    def __init__(self):
        self.telegram_bot = TelegramBot()
        self.flask_app = app
        
    def run_flask(self):
        """Run Flask server in a separate thread"""
        self.flask_app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
    
    def start(self):
        """Start both Flask webhook server and Telegram bot"""
        logger.info("Starting Trading Bot...")
        
        # Start Flask server in a separate thread
        flask_thread = threading.Thread(target=self.run_flask)
        flask_thread.daemon = True
        flask_thread.start()
        logger.info("Flask webhook server started on port 5000")
        
        # Give Flask a moment to start
        time.sleep(1)
        
        # Start Telegram bot in main thread
        logger.info("Starting Telegram bot...")
        asyncio.run(self.telegram_bot.start_polling())

if __name__ == "__main__":
    if not Config.BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        exit(1)
    
    bot = TradingBot()
    try:
        bot.start()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        exit(1)