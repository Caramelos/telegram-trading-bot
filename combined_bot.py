#!/usr/bin/env python3
import asyncio
import logging
import json
import os
import random
import threading
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from flask import Flask, request, jsonify
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for webhook
app = Flask(__name__)

# User state storage (in production, use a database)
user_states = {}

# Joke collection for the joke bot
JOKES = [
    "Why don't traders ever play poker? Because they're always folding!",
    "What do you call a sleeping trader? A nap trade!",
    "Why did the trader break up with the stock? It was too volatile!",
    "What's a trader's favorite type of music? Bull market blues!",
    "Why don't day traders ever get married? They're commitment-phobic!",
    "What do you call a trader who went broke? Bearish on life!",
    "Why did the Bitcoin go to therapy? It had too many ups and downs!",
    "What's the difference between a trader and a pizza? A pizza can feed a family!",
    "Why don't traders trust stairs? They're always looking for support and resistance!",
    "What did the trader say when his wife asked for money? 'Sorry honey, I'm all in!'",
    "Why did the technical analyst bring a ladder to work? To reach the resistance level!",
    "What's a bear market's favorite drink? Short-espresso!",
    "Why don't crypto traders sleep? Because the market never closes... oh wait!",
    "What do you call a profitable trader? Lucky!",
    "Why did the swing trader go to the park? To practice holding!",
]

# Current active strategies (this would come from TradingView in production)
ACTIVE_STRATEGIES = {
    "BTC 5min Price Feed": {
        "symbol": "BTCUSD", 
        "timeframe": "5m",
        "status": "Active",
        "last_signal": "Price Update",
        "description": "Real-time BTC price monitoring every 5 minutes"
    },
    "EMA Cross Strategy": {
        "symbol": "ETHUSD",
        "timeframe": "15m", 
        "status": "Active",
        "last_signal": "Buy Signal",
        "description": "EMA 21/50 crossover strategy for ETH"
    },
    "RSI Divergence": {
        "symbol": "ADAUSD",
        "timeframe": "1h",
        "status": "Paused", 
        "last_signal": "Sell Signal",
        "description": "RSI divergence detection for ADA"
    }
}

# Global telegram application variable
telegram_app = None

class UserState:
    def __init__(self, user_id):
        self.user_id = user_id
        self.notifications_enabled = True
        self.price_alerts_enabled = True
        self.signal_alerts_enabled = True
        self.last_btc_price = None
        
    def to_dict(self):
        return {
            'user_id': self.user_id,
            'notifications_enabled': self.notifications_enabled,
            'price_alerts_enabled': self.price_alerts_enabled,
            'signal_alerts_enabled': self.signal_alerts_enabled,
            'last_btc_price': self.last_btc_price
        }

def get_user_state(user_id):
    if user_id not in user_states:
        user_states[user_id] = UserState(user_id)
    return user_states[user_id]

def create_main_menu():
    """Create the main menu keyboard"""
    keyboard = [
        [
            InlineKeyboardButton("📈 Current Strategy", callback_data="menu_strategy"),
            InlineKeyboardButton("😂 Joke Bot", callback_data="menu_joke")
        ],
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="menu_notifications"),
            InlineKeyboardButton("📊 Price Check", callback_data="menu_price")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("📈 Status", callback_data="menu_status")
        ],
        [
            InlineKeyboardButton("ℹ️ Help", callback_data="menu_help"),
            InlineKeyboardButton("🧪 Test Signal", callback_data="menu_test")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_notifications_menu(user_state):
    """Create notifications control menu"""
    status_icon = "🟢" if user_state.notifications_enabled else "🔴"
    price_icon = "🟢" if user_state.price_alerts_enabled else "🔴"
    signal_icon = "🟢" if user_state.signal_alerts_enabled else "🔴"
    
    keyboard = [
        [InlineKeyboardButton(f"{status_icon} All Notifications", callback_data="toggle_all_notifications")],
        [InlineKeyboardButton(f"{price_icon} Price Alerts", callback_data="toggle_price_alerts")],
        [InlineKeyboardButton(f"{signal_icon} Trading Signals", callback_data="toggle_signal_alerts")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

def create_settings_menu():
    """Create settings menu"""
    keyboard = [
        [
            InlineKeyboardButton("🎯 Alert Frequency", callback_data="settings_frequency"),
            InlineKeyboardButton("💰 Price Thresholds", callback_data="settings_thresholds")
        ],
        [
            InlineKeyboardButton("📱 Message Format", callback_data="settings_format"),
            InlineKeyboardButton("🔒 Security", callback_data="settings_security")
        ],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Telegram Bot Functions
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    user_state = get_user_state(user.id)
    
    welcome_text = f"""
🤖 **Welcome to TradePods Bot!**

Hello {user.first_name}! Your trading signal bot is ready.

**What I can do:**
🔔 Send you TradingView alerts
📊 Show live BTC prices  
📈 Track your trading signals
⚙️ Customizable notifications
😂 Tell you trading jokes!

**Your Chat ID:** `{user.id}`

Choose an option from the menu below:
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_menu(),
        parse_mode='Markdown'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    await update.message.reply_text(
        "🎛️ **Main Menu**\n\nChoose an option:",
        reply_markup=create_main_menu(),
        parse_mode='Markdown'
    )

async def get_btc_price():
    """Fetch current BTC price from a public API"""
    try:
        response = requests.get('https://api.coinbase.com/v2/exchange-rates?currency=BTC', timeout=5)
        data = response.json()
        btc_price = float(data['data']['rates']['USD'])
        return btc_price
    except Exception as e:
        logger.error(f"Error fetching BTC price: {e}")
        return None

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_state = get_user_state(user_id)
    data = query.data
    
    if data == "menu_strategy":
        text = """
📈 **Current Trading Strategies**

Here are your active TradingView strategies:
        """
        
        for name, strategy in ACTIVE_STRATEGIES.items():
            status_icon = "🟢" if strategy["status"] == "Active" else "🟡" if strategy["status"] == "Paused" else "🔴"
            text += f"""
{status_icon} **{name}**
• Symbol: {strategy["symbol"]}
• Timeframe: {strategy["timeframe"]}
• Status: {strategy["status"]}
• Last Signal: {strategy["last_signal"]}
• Description: {strategy["description"]}
            """
        
        text += f"""

📊 **Total Strategies:** {len(ACTIVE_STRATEGIES)}
✅ **Active:** {sum(1 for s in ACTIVE_STRATEGIES.values() if s['status'] == 'Active')}
⏸️ **Paused:** {sum(1 for s in ACTIVE_STRATEGIES.values() if s['status'] == 'Paused')}

💡 Add more strategies in TradingView with your webhook URL
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh", callback_data="menu_strategy")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_joke":
        joke = random.choice(JOKES)
        
        text = f"""
😂 **Trading Joke of the Day**

{joke}

😄 Want another one? Just tap the button again!

*Laughter is the best trading strategy... just kidding, please don't trade based on jokes!*
        """
        
        keyboard = [
            [InlineKeyboardButton("😂 Another Joke!", callback_data="menu_joke")],
            [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
        ]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_price":
        btc_price = await get_btc_price()
        if btc_price:
            price_change = ""
            if user_state.last_btc_price:
                change = btc_price - user_state.last_btc_price
                change_pct = (change / user_state.last_btc_price) * 100
                arrow = "📈" if change > 0 else "📉" if change < 0 else "➡️"
                price_change = f"\n{arrow} Change: ${change:+.2f} ({change_pct:+.2f}%)"
            
            user_state.last_btc_price = btc_price
            
            text = f"""
💰 **Live BTC Price**

**Current Price:** ${btc_price:,.2f}{price_change}

📊 **Market Info:**
• Exchange: Coinbase
• Updated: {datetime.now().strftime('%H:%M:%S')}

🔄 Tap "Refresh" for latest price
            """
            
            keyboard = [
                [InlineKeyboardButton("🔄 Refresh", callback_data="menu_price")],
                [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]
            ]
            
        else:
            text = "❌ Unable to fetch BTC price. Please try again."
            keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]]
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    elif data == "menu_test":
        text = """
🧪 **Test Signal Sent!**

A test trading signal has been sent to demonstrate the format.

If you received a test message, your bot is working correctly!
        """
        keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_main")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
        # Send test signal
        test_signal = f"""
🧪 **TEST SIGNAL**

📊 Symbol: BTCUSD
🎯 Action: TEST
💰 Price: $67,500
📈 Strategy: Bot Test

⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

✅ Your bot is working correctly!
        """
        await context.bot.send_message(chat_id=user_id, text=test_signal, parse_mode='Markdown')
    
    elif data == "back_to_main":
        await query.edit_message_text(
            "🎛️ **Main Menu**\n\nChoose an option:",
            reply_markup=create_main_menu(),
            parse_mode='Markdown'
        )

# Flask webhook endpoints
def should_send_message(chat_id, message_type="signal"):
    """Check if user wants to receive this type of message"""
    user_state = get_user_state(chat_id)
    
    if not user_state.notifications_enabled:
        return False
    
    if message_type == "price" and not user_state.price_alerts_enabled:
        return False
    
    if message_type == "signal" and not user_state.signal_alerts_enabled:
        return False
    
    return True

def send_telegram_message_sync(chat_id, message, message_type="signal"):
    """Send message to Telegram using the bot"""
    global telegram_app
    
    if not should_send_message(chat_id, message_type):
        logger.info(f"Message blocked by user preferences for chat {chat_id}")
        return True
    
    if telegram_app:
        # Schedule the message to be sent
        asyncio.create_task(telegram_app.bot.send_message(
            chat_id=chat_id, 
            text=message, 
            parse_mode='HTML'
        ))
        return True
    return False

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive TradingView webhook alerts"""
    try:
        data = request.get_json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        # Verify webhook secret
        if Config.WEBHOOK_SECRET and Config.WEBHOOK_SECRET != "default_secret":
            received_secret = data.get('secret')
            if received_secret != Config.WEBHOOK_SECRET:
                return jsonify({"error": "Invalid secret"}), 401
        
        # Format the signal message
        action = data.get('action', '').upper()
        symbol = data.get('symbol', data.get('ticker', 'Unknown'))
        price = data.get('price', data.get('close', 'N/A'))
        strategy = data.get('strategy', data.get('indicator', 'Manual Alert'))
        message = data.get('message', data.get('comment', ''))
        
        if ':' in symbol:
            symbol = symbol.split(':')[-1]
        
        emoji = '💰📊' if action in ['PRICE_UPDATE', 'PRICE_MOVEMENT'] else '🟢📈' if action in ['BUY', 'LONG'] else '🔴📉' if action in ['SELL', 'SHORT'] else '🔔'
        
        formatted_message = f"""
{emoji} <b>TRADING SIGNAL</b>

📊 <b>Symbol:</b> {symbol}
🎯 <b>Action:</b> {action}
💰 <b>Price:</b> ${price}
📈 <b>Strategy:</b> {strategy}

{'📝 <b>Details:</b> ' + message if message else ''}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 <i>Use /menu to control notifications</i>
        """
        
        # Send to allowed chat IDs
        message_type = "price" if action in ['PRICE_UPDATE', 'PRICE_MOVEMENT'] else "signal"
        sent_count = 0
        
        for chat_id in Config.ALLOWED_CHAT_IDS:
            if send_telegram_message_sync(chat_id, formatted_message, message_type):
                sent_count += 1
        
        return jsonify({
            "status": "success",
            "message": f"Signal sent to {sent_count} chats",
            "symbol": symbol
        }), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "3.0 Combined Bot + Webhook",
        "features": {
            "telegram_bot": True,
            "webhook_server": True,
            "user_preferences": True,
            "strategy_display": True,
            "joke_bot": True
        }
    })

async def setup_telegram_bot():
    """Set up the Telegram bot"""
    global telegram_app
    
    # Create application
    telegram_app = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add handlers
    telegram_app.add_handler(CommandHandler("start", start_command))
    telegram_app.add_handler(CommandHandler("menu", menu_command))
    telegram_app.add_handler(CallbackQueryHandler(button_callback))
    
    # Set bot commands
    commands = [
        BotCommand("start", "Start the bot and show welcome message"),
        BotCommand("menu", "Show the main menu"),
    ]
    await telegram_app.bot.set_my_commands(commands)
    
    logger.info("Telegram bot setup complete")
    return telegram_app

def run_flask_app():
    """Run the Flask webhook server"""
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"Starting Flask webhook server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)

async def run_telegram_bot():
    """Run the Telegram bot"""
    logger.info("Starting Telegram bot...")
    await telegram_app.run_polling(allowed_updates=Update.ALL_TYPES)

async def main():
    """Main function to run both Flask and Telegram bot"""
    # Setup Telegram bot
    await setup_telegram_bot()
    
    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    # Run Telegram bot
    await run_telegram_bot()

if __name__ == '__main__':
    asyncio.run(main())