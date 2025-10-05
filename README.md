# Telegram Trading Bot

A Python-based Telegram bot that receives trading signals from TradingView webhooks and forwards them to authorized Telegram users.

## Features

- 📊 Receives TradingView webhook alerts
- 🤖 Sends formatted trading signals to Telegram
- 🔒 Token and strategy filtering
- 👥 Multi-user support with chat ID authorization
- 🛡️ Webhook secret validation
- 📈 Support for BUY/SELL/LONG/SHORT signals

## Setup

### 1. Create a Telegram Bot

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command and follow instructions
3. Save the bot token

### 2. Get Your Chat ID

1. Start a chat with your bot
2. Send `/start` command
3. Use `/status` command to see your Chat ID

### 3. Environment Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your values:
   ```
   BOT_TOKEN=your_telegram_bot_token_here
   WEBHOOK_SECRET=your_webhook_secret_key_here
   ALLOWED_CHAT_IDS=123456789,987654321
   WEBHOOK_URL=https://your-domain.com/webhook
   ALLOWED_TOKENS=BTCUSD,ETHUSD,ADAUSD
   ALLOWED_STRATEGIES=EMA_Cross,RSI_Divergence
   ```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Bot

```bash
python main.py
```

## TradingView Webhook Setup

1. In TradingView, create an alert
2. In the "Notifications" tab, check "Webhook URL"
3. Enter your webhook URL: `https://your-domain.com/webhook`
4. Set the JSON message format:

```json
{
  "secret": "your_webhook_secret_key_here",
  "action": "{{strategy.order.action}}",
  "token": "{{ticker}}",
  "strategy": "Your Strategy Name",
  "price": "{{close}}",
  "exchange": "{{exchange}}",
  "message": "{{strategy.order.comment}}",
  "timestamp": "{{time}}"
}
```

## Webhook Message Format

The bot accepts the following JSON format from TradingView:

```json
{
  "secret": "your_secret_key",
  "action": "BUY",
  "token": "BTCUSD",
  "strategy": "EMA_Cross",
  "price": "45000",
  "exchange": "Binance",
  "message": "EMA crossover detected",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help message
- `/status` - Check bot status and authorization

## Deployment

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
```

### Using Heroku

1. Install Heroku CLI
2. Create a `Procfile`:
   ```
   web: gunicorn webhook_server:app
   worker: python main.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   heroku config:set BOT_TOKEN=your_token
   heroku config:set WEBHOOK_SECRET=your_secret
   git push heroku main
   ```

## Security

- Always use a strong webhook secret
- Restrict `ALLOWED_CHAT_IDS` to authorized users only
- Use HTTPS for webhook endpoints
- Keep your bot token secure

## Troubleshooting

1. **Bot not responding**: Check if `BOT_TOKEN` is correct
2. **Webhook not working**: Verify URL is accessible and uses HTTPS
3. **Signals not filtered**: Check `ALLOWED_TOKENS` and `ALLOWED_STRATEGIES` configuration
4. **Unauthorized access**: Ensure your Chat ID is in `ALLOWED_CHAT_IDS`

## License

MIT License