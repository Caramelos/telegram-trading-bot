from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
from config import Config
from signal_processor import SignalProcessor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
signal_processor = SignalProcessor()

@app.route('/webhook', methods=['POST'])
async def webhook():
    """Receive TradingView webhook alerts"""
    try:
        # Verify content type
        if not request.is_json:
            logger.warning("Received non-JSON request")
            return jsonify({"error": "Content-Type must be application/json"}), 400
        
        data = request.get_json()
        logger.info(f"Received webhook data: {data}")
        
        # Verify webhook secret if configured
        if Config.WEBHOOK_SECRET and Config.WEBHOOK_SECRET != "default_secret":
            received_secret = data.get('secret')
            if received_secret != Config.WEBHOOK_SECRET:
                logger.warning("Invalid webhook secret")
                return jsonify({"error": "Invalid secret"}), 401
        
        # Process the signal
        processed = await signal_processor.process_signal(data)
        
        if processed:
            return jsonify({"status": "success", "message": "Signal processed"}), 200
        else:
            return jsonify({"status": "filtered", "message": "Signal filtered out"}), 200
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "allowed_tokens": len(Config.ALLOWED_TOKENS),
        "allowed_strategies": len(Config.ALLOWED_STRATEGIES)
    })

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic info"""
    return jsonify({
        "service": "TradingView Telegram Bot",
        "status": "running",
        "webhook_endpoint": "/webhook",
        "health_endpoint": "/health"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)