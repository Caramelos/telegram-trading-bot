# TradingView Integration Guide

## 🎯 Complete Setup Instructions for Automated Trading Signals

### Step 1: Get Your Chat ID

1. **Start your bot:** https://t.me/tradepods_bot
2. **Send `/start` command** - the bot will show your Chat ID
3. **Copy your Chat ID** (example: 123456789)

### Step 2: Configure Your Bot

1. **Edit your .env file:**
   ```bash
   cd /Users/shuang/Desktop/telegram-trading-bot
   nano .env
   ```

2. **Add your Chat ID:**
   ```
   BOT_TOKEN=8357026148:AAHoQhclTPy1L2Q7DYcdxwjWtrdeqBlSyOA
   WEBHOOK_SECRET=tradepods_secret_2025
   ALLOWED_CHAT_IDS=YOUR_CHAT_ID_HERE
   WEBHOOK_URL=https://your-domain.com/webhook
   ALLOWED_TOKENS=BTCUSD,ETHUSD,ADAUSD,SOLUSD,DOGEUSDT
   ALLOWED_STRATEGIES=EMA Cross,RSI Levels,MACD,Support/Resistance
   ```

### Step 3: Start Your Webhook Server

```bash
cd /Users/shuang/Desktop/telegram-trading-bot
python webhook_server_standalone.py
```

The server will run on: http://localhost:8080

### Step 4: Make Your Webhook Public (Choose One Option)

#### Option A: Using ngrok (Recommended for Testing)
```bash
# Install ngrok if you haven't
brew install ngrok

# Expose your local server
ngrok http 8080
```
Copy the HTTPS URL (e.g., `https://abc123.ngrok.io`)

#### Option B: Deploy to Cloud (Production)
- Deploy to Heroku, Railway, or any cloud provider
- Make sure your webhook endpoint is publicly accessible via HTTPS

### Step 5: Set Up TradingView Alerts

#### Method 1: Using Pine Script (Automated for Watchlist)

1. **Copy the Pine Script:**
   - Use `multi_strategy_alerts.pine` from the scripts folder
   - Or use `ema_rsi_strategy.pine` for EMA + RSI strategy

2. **Add to TradingView:**
   - Open TradingView
   - Go to Pine Editor (bottom panel)
   - Paste the script
   - Click "Add to Chart"

3. **Configure the Script:**
   - Set your `webhook_secret` to: `tradepods_secret_2025`
   - Choose your preferred strategy
   - Adjust indicator parameters

4. **Create Alerts:**
   - Right-click on chart → "Add Alert"
   - Condition: Select your script
   - Actions: ✅ Webhook URL
   - Webhook URL: `https://your-ngrok-url.ngrok.io/webhook`
   - Message: Use the default (script handles JSON formatting)
   - Click "Create"

#### Method 2: Manual Alerts for Any Indicator

1. **Create Alert on Any Indicator:**
   - Add any indicator to chart (RSI, MACD, etc.)
   - Right-click indicator → "Add Alert"

2. **Webhook Setup:**
   - Actions: ✅ Webhook URL  
   - Webhook URL: `https://your-ngrok-url.ngrok.io/webhook`
   - Message (use this JSON template):
   ```json
   {
     "secret": "tradepods_secret_2025",
     "action": "BUY",
     "symbol": "{{ticker}}",
     "price": "{{close}}",
     "strategy": "Manual Alert",
     "exchange": "{{exchange}}",
     "message": "Alert triggered: {{alert_message}}",
     "timestamp": "{{time}}"
   }
   ```

### Step 6: Test Your Setup

1. **Test webhook server:**
   ```bash
   curl -X GET http://localhost:8080/test
   ```

2. **Test with sample signal:**
   ```bash
   curl -X POST http://localhost:8080/webhook \
   -H "Content-Type: application/json" \
   -d '{
     "secret": "tradepods_secret_2025",
     "action": "BUY", 
     "symbol": "BTCUSD",
     "price": "67500",
     "strategy": "Test Alert"
   }'
   ```

3. **Check your Telegram** - you should receive the signal!

### Step 7: Apply to Your Entire Watchlist

#### For Automated Signals:
1. **Add the Pine Script to multiple charts:**
   - Open each symbol in your watchlist
   - Add the Pine Script indicator
   - Create alerts for each chart

2. **Bulk Alert Creation:**
   - Use TradingView's "Alert Manager"
   - Create similar alerts for all symbols
   - Each alert uses the same webhook URL

#### For Manual Monitoring:
- Set up alerts on key levels/indicators
- Use the JSON template for consistent formatting
- Customize the "action" field (BUY/SELL) based on your analysis

## 🎛️ Advanced Configuration

### Custom Signal Filtering

Edit your `.env` file to filter signals:

```bash
# Only receive signals for these tokens
ALLOWED_TOKENS=BTCUSD,ETHUSD,ADAUSD

# Only receive signals from these strategies  
ALLOWED_STRATEGIES=EMA Cross,RSI Levels

# Multiple chat IDs (comma-separated)
ALLOWED_CHAT_IDS=123456789,987654321
```

### Multiple Timeframes

Create alerts on different timeframes:
- 1m, 5m, 15m for scalping
- 1h, 4h for swing trading
- 1d for position trading

Each alert will specify the timeframe in the message.

## 🔧 Troubleshooting

1. **No signals received:**
   - Check webhook server is running
   - Verify ngrok URL is correct
   - Check TradingView alert is active
   - Verify your Chat ID in .env

2. **Signals filtered out:**
   - Check ALLOWED_TOKENS and ALLOWED_STRATEGIES
   - Look at server logs for filtering messages

3. **Webhook errors:**
   - Check webhook secret matches
   - Verify JSON format in alert message
   - Check server logs for detailed errors

## 🚀 You're Ready!

Once set up, your bot will automatically:
✅ Monitor your TradingView watchlist
✅ Send instant buy/sell signals to Telegram  
✅ Filter signals based on your preferences
✅ Work 24/7 even when you're away

Your trading signals will look like this in Telegram:

```
🟢📈 TRADING SIGNAL

📊 Symbol: BTCUSD
🎯 Action: BUY
💰 Price: $67,500
📈 Strategy: EMA Cross
🏢 Exchange: BINANCE

📝 Details: Fast EMA crossed above Slow EMA with RSI confirmation

⏰ Time: 2025-10-03 18:30:15
```