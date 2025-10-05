import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "default_secret")
    ALLOWED_CHAT_IDS = [int(id.strip()) for id in os.getenv("ALLOWED_CHAT_IDS", "").split(",") if id.strip()]
    WEBHOOK_URL = os.getenv("WEBHOOK_URL")
    
    # TradingView signal filtering
    ALLOWED_TOKENS = os.getenv("ALLOWED_TOKENS", "").split(",") if os.getenv("ALLOWED_TOKENS") else []
    ALLOWED_STRATEGIES = os.getenv("ALLOWED_STRATEGIES", "").split(",") if os.getenv("ALLOWED_STRATEGIES") else []