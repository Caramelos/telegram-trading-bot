#!/usr/bin/env python3
import asyncio
import logging
import json
import os
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# User state storage (in production, use a database)
user_states = {}

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

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_state = get_user_state(update.effective_user.id)
    
    status_text = f"""
📊 **Bot Status**

🤖 **System:** Online ✅
🔔 **Notifications:** {'✅ Enabled' if user_state.notifications_enabled else '❌ Disabled'}
📈 **Price Alerts:** {'✅ Enabled' if user_state.price_alerts_enabled else '❌ Disabled'}
🎯 **Signal Alerts:** {'✅ Enabled' if user_state.signal_alerts_enabled else '❌ Disabled'}

🌐 **Webhook:** Active
🔗 **TradingView:** Connected
⏰ **Last Update:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

💡 Use /menu to access controls
    """
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

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
    
    if data == "menu_notifications":
        text = f"""
🔔 **Notification Settings**

Control what alerts you receive:

🟢 = Enabled  🔴 = Disabled

Current Status:
• All Notifications: {'🟢 ON' if user_state.notifications_enabled else '🔴 OFF'}
• Price Alerts: {'🟢 ON' if user_state.price_alerts_enabled else '🔴 OFF'}  
• Trading Signals: {'🟢 ON' if user_state.signal_alerts_enabled else '🔴 OFF'}
        """
        await query.edit_message_text(
            text,
            reply_markup=create_notifications_menu(user_state),
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
    
    elif data == "menu_settings":
        text = """
⚙️ **Settings**

Customize your trading bot experience:

🎯 **Alert Frequency** - How often you get updates
💰 **Price Thresholds** - Set price alert levels  
📱 **Message Format** - Customize alert appearance
🔒 **Security** - Webhook and authentication settings
        """
        await query.edit_message_text(
            text,
            reply_markup=create_settings_menu(),
            parse_mode='Markdown'
        )
    
    elif data == "menu_status":
        await status_command(query, context)
        
    elif data == "menu_help":
        text = """
ℹ️ **Help & Commands**

**Available Commands:**
• `/start` - Welcome message and setup
• `/menu` - Show main menu
• `/status` - Check bot status
• `/help` - Show this help message

**How to Connect TradingView:**
1. Create alert in TradingView
2. Set webhook URL: `https://web-production-ae76.up.railway.app/webhook`
3. Use this message format:
```
{"secret":"tradepods_secret_2025","action":"{{strategy.order.action}}","symbol":"{{ticker}}","price":"{{close}}","strategy":"Your Strategy"}
```

**Need Support?**
Contact the bot administrator or check documentation.
        """
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

You can also test by visiting:
`https://web-production-ae76.up.railway.app/test`
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
    
    elif data == "toggle_all_notifications":
        user_state.notifications_enabled = not user_state.notifications_enabled
        status = "enabled" if user_state.notifications_enabled else "disabled"
        
        await query.edit_message_text(
            f"🔔 All notifications have been **{status}**",
            reply_markup=create_notifications_menu(user_state),
            parse_mode='Markdown'
        )
    
    elif data == "toggle_price_alerts":
        user_state.price_alerts_enabled = not user_state.price_alerts_enabled
        status = "enabled" if user_state.price_alerts_enabled else "disabled"
        
        await query.edit_message_text(
            f"📊 Price alerts have been **{status}**",
            reply_markup=create_notifications_menu(user_state),
            parse_mode='Markdown'
        )
    
    elif data == "toggle_signal_alerts":
        user_state.signal_alerts_enabled = not user_state.signal_alerts_enabled
        status = "enabled" if user_state.signal_alerts_enabled else "disabled"
        
        await query.edit_message_text(
            f"📈 Trading signal alerts have been **{status}**",
            reply_markup=create_notifications_menu(user_state),
            parse_mode='Markdown'
        )
    
    elif data == "back_to_main":
        await query.edit_message_text(
            "🎛️ **Main Menu**\n\nChoose an option:",
            reply_markup=create_main_menu(),
            parse_mode='Markdown'
        )
    
    # Settings callbacks
    elif data.startswith("settings_"):
        setting = data.replace("settings_", "")
        text = f"⚙️ **{setting.title()} Settings**\n\nThis feature is coming soon!"
        keyboard = [[InlineKeyboardButton("⬅️ Back to Settings", callback_data="menu_settings")]]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

def should_send_message(user_id, message_type="signal"):
    """Check if user wants to receive this type of message"""
    user_state = get_user_state(user_id)
    
    if not user_state.notifications_enabled:
        return False
    
    if message_type == "price" and not user_state.price_alerts_enabled:
        return False
    
    if message_type == "signal" and not user_state.signal_alerts_enabled:
        return False
    
    return True

async def main():
    """Main function to run the bot"""
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("help", menu_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Set bot commands for menu
    commands = [
        BotCommand("start", "Start the bot and show welcome message"),
        BotCommand("menu", "Show the main menu"),
        BotCommand("status", "Check bot status"),
        BotCommand("help", "Show help information"),
    ]
    
    await application.bot.set_my_commands(commands)
    
    # Start the bot
    logger.info("Enhanced TradePods Bot starting...")
    await application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    asyncio.run(main())