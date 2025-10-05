import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text(
            "🤖 Trading Signal Bot Started!\n\n"
            "This bot will send you trading signals from TradingView.\n"
            "Use /help for available commands."
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        help_text = """
🔧 Available Commands:
/start - Start the bot
/help - Show this help message  
/status - Check bot status

📊 This bot receives trading signals from TradingView and forwards them to authorized users.
        """
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id = update.effective_chat.id
        is_authorized = chat_id in Config.ALLOWED_CHAT_IDS if Config.ALLOWED_CHAT_IDS else True
        
        status_text = f"""
📊 Bot Status:
Chat ID: {chat_id}
Authorized: {'✅' if is_authorized else '❌'}
Allowed Tokens: {len(Config.ALLOWED_TOKENS)} configured
Allowed Strategies: {len(Config.ALLOWED_STRATEGIES)} configured
        """
        await update.message.reply_text(status_text)
    
    async def send_signal(self, signal_data: dict):
        """Send trading signal to all authorized chats"""
        for chat_id in Config.ALLOWED_CHAT_IDS:
            try:
                await self.application.bot.send_message(
                    chat_id=chat_id,
                    text=self.format_signal_message(signal_data),
                    parse_mode='HTML'
                )
                logger.info(f"Signal sent to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send signal to chat {chat_id}: {e}")
    
    def format_signal_message(self, signal: dict) -> str:
        """Format trading signal for Telegram message"""
        emoji_map = {
            'BUY': '🟢',
            'SELL': '🔴',
            'LONG': '📈',
            'SHORT': '📉'
        }
        
        action = signal.get('action', '').upper()
        emoji = emoji_map.get(action, '🔔')
        
        message = f"""
{emoji} <b>Trading Signal</b>

📊 <b>Token:</b> {signal.get('token', 'N/A')}
🎯 <b>Action:</b> {action}
📈 <b>Strategy:</b> {signal.get('strategy', 'N/A')}
💰 <b>Price:</b> {signal.get('price', 'N/A')}

📝 <b>Details:</b>
{signal.get('message', 'No additional details')}

⏰ <b>Time:</b> {signal.get('timestamp', 'N/A')}
        """
        return message.strip()
    
    async def start_polling(self):
        """Start the bot with polling"""
        logger.info("Starting bot with polling...")
        await self.application.run_polling()
    
    def get_application(self):
        """Get the application instance for webhook setup"""
        return self.application