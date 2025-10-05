#!/usr/bin/env python3
import asyncio
import logging
from flask import Flask, request, jsonify
from datetime import datetime
import json
import requests
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Store for bot token to send messages
BOT_TOKEN = Config.BOT_TOKEN
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_telegram_message(chat_id, message):
    """Send message to Telegram chat"""
    try:
        url = f"{TELEGRAM_API_URL}/sendMessage"
        data = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': 'HTML'
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            logger.info(f"Message sent successfully to chat {chat_id}")
            return True
        else:
            logger.error(f"Failed to send message: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending Telegram message: {e}")
        return False

def format_trading_signal(data):
    """Format TradingView signal into readable message"""
    
    # Extract signal data
    action = data.get('action', '').upper()
    symbol = data.get('symbol', data.get('ticker', 'Unknown'))
    price = data.get('price', data.get('close', 'N/A'))
    strategy = data.get('strategy', data.get('indicator', 'Manual Alert'))
    exchange = data.get('exchange', '')
    message = data.get('message', data.get('comment', ''))
    
    # Remove exchange prefix if present (e.g., "BINANCE:BTCUSDT" -> "BTCUSDT")
    if ':' in symbol:
        symbol = symbol.split(':')[-1]
    
    # Choose emoji based on action
    if action in ['BUY', 'LONG']:
        emoji = '🟢📈'
        action_text = f"🟢 **{action}**"
    elif action in ['SELL', 'SHORT']:
        emoji = '🔴📉'  
        action_text = f"🔴 **{action}**"
    else:
        emoji = '🔔'
        action_text = f"🔔 **{action}**"
    
    # Format the message
    formatted_message = f"""
{emoji} <b>TRADING SIGNAL</b>

📊 <b>Symbol:</b> {symbol}
🎯 <b>Action:</b> {action}
💰 <b>Price:</b> ${price}
📈 <b>Strategy:</b> {strategy}
{f'🏢 <b>Exchange:</b> {exchange}' if exchange else ''}

{'📝 <b>Details:</b> ' + message if message else ''}

⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    return formatted_message.strip()

def should_process_signal(data):
    """Check if signal should be processed based on filters"""
    
    # Get symbol and remove exchange prefix
    symbol = data.get('symbol', data.get('ticker', ''))
    if ':' in symbol:
        symbol = symbol.split(':')[-1]
    
    # Check allowed tokens filter
    if Config.ALLOWED_TOKENS:
        allowed_upper = [token.upper().strip() for token in Config.ALLOWED_TOKENS if token.strip()]
        if symbol.upper() not in allowed_upper:
            logger.info(f"Symbol {symbol} not in allowed tokens: {allowed_upper}")
            return False
    
    # Check allowed strategies filter  
    strategy = data.get('strategy', data.get('indicator', ''))
    if Config.ALLOWED_STRATEGIES and strategy:
        allowed_strategies_upper = [s.upper().strip() for s in Config.ALLOWED_STRATEGIES if s.strip()]
        if strategy.upper() not in allowed_strategies_upper:
            logger.info(f"Strategy {strategy} not in allowed strategies: {allowed_strategies_upper}")
            return False
    
    return True

@app.route('/webhook', methods=['POST'])
def webhook():
    """Receive TradingView webhook alerts"""
    try:
        # Check content type
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
        
        # Verify webhook secret if configured
        if Config.WEBHOOK_SECRET and Config.WEBHOOK_SECRET != "default_secret":
            received_secret = data.get('secret')
            if received_secret != Config.WEBHOOK_SECRET:
                logger.warning(f"Invalid webhook secret received: {received_secret}")
                return jsonify({"error": "Invalid secret"}), 401
        
        # Check if signal should be processed
        if not should_process_signal(data):
            return jsonify({"status": "filtered", "message": "Signal filtered out"}), 200
        
        # Format the signal message
        formatted_message = format_trading_signal(data)
        
        # Send to all allowed chat IDs
        if Config.ALLOWED_CHAT_IDS:
            sent_count = 0
            for chat_id in Config.ALLOWED_CHAT_IDS:
                if send_telegram_message(chat_id, formatted_message):
                    sent_count += 1
            
            return jsonify({
                "status": "success",
                "message": f"Signal sent to {sent_count} chats",
                "symbol": data.get('symbol', 'Unknown')
            }), 200
        else:
            logger.warning("No ALLOWED_CHAT_IDS configured")
            return jsonify({
                "status": "warning", 
                "message": "No chat IDs configured to receive signals"
            }), 200
            
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/test', methods=['POST', 'GET'])
def test_endpoint():
    """Test endpoint for manual signal testing"""
    
    # Sample test signal
    test_signal = {
        "secret": Config.WEBHOOK_SECRET,
        "action": "BUY",
        "symbol": "BTCUSD",
        "price": "67500",
        "strategy": "Test Signal",
        "message": "This is a test signal from your webhook server"
    }
    
    if request.method == 'POST':
        # Use provided data or test data
        data = request.get_json() if request.is_json else test_signal
    else:
        # GET request - use test data
        data = test_signal
    
    # Process the test signal
    if should_process_signal(data):
        formatted_message = format_trading_signal(data)
        
        if Config.ALLOWED_CHAT_IDS:
            sent_count = 0
            for chat_id in Config.ALLOWED_CHAT_IDS:
                if send_telegram_message(chat_id, formatted_message):
                    sent_count += 1
            
            return jsonify({
                "status": "success",
                "message": f"Test signal sent to {sent_count} chats",
                "formatted_message": formatted_message
            }), 200
        else:
            return jsonify({
                "status": "warning",
                "message": "No chat IDs configured",
                "formatted_message": formatted_message
            }), 200
    else:
        return jsonify({
            "status": "filtered",
            "message": "Test signal was filtered out"
        }), 200

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "allowed_tokens": len(Config.ALLOWED_TOKENS),
            "allowed_strategies": len(Config.ALLOWED_STRATEGIES), 
            "allowed_chats": len(Config.ALLOWED_CHAT_IDS),
            "webhook_secret_configured": bool(Config.WEBHOOK_SECRET and Config.WEBHOOK_SECRET != "default_secret")
        }
    })

@app.route('/', methods=['GET'])
def home():
    """Home endpoint with information"""
    return jsonify({
        "service": "TradingView Telegram Bot Webhook Server",
        "status": "running",
        "endpoints": {
            "webhook": "/webhook (POST) - Receive TradingView alerts",
            "test": "/test (GET/POST) - Test signal sending", 
            "health": "/health (GET) - Health check"
        },
        "bot_username": "@tradepods_bot"
    })

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 8080))
    logger.info("Starting TradingView Webhook Server...")
    logger.info(f"Server will run on port {port}")
    logger.info(f"Webhook endpoint: /webhook")
    logger.info(f"Test endpoint: /test")
    
    app.run(host='0.0.0.0', port=port, debug=False)