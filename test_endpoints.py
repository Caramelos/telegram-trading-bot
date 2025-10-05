import requests
import json

def test_webhook_endpoint():
    """Test the webhook endpoint with sample data"""
    
    # Sample TradingView webhook payload
    test_payload = {
        "secret": "test_secret_123",
        "action": "BUY",
        "token": "BTCUSD", 
        "strategy": "EMA_Cross",
        "price": "45000",
        "exchange": "Binance",
        "message": "Strong bullish signal detected",
        "timestamp": "2025-01-01T12:00:00Z"
    }
    
    # Test webhook endpoint
    webhook_url = "http://localhost:5000/webhook"
    
    try:
        response = requests.post(
            webhook_url,
            json=test_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook test successful!")
        else:
            print("❌ Webhook test failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to webhook server. Make sure the bot is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing webhook: {e}")

def test_health_endpoint():
    """Test the health check endpoint"""
    
    health_url = "http://localhost:5000/health"
    
    try:
        response = requests.get(health_url, timeout=10)
        print(f"Health Check Status: {response.status_code}")
        print(f"Health Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check successful!")
        else:
            print("❌ Health check failed!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Make sure the bot is running on localhost:5000")
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")

if __name__ == "__main__":
    print("Testing Trading Bot Endpoints...")
    print("=" * 50)
    
    print("\n1. Testing Health Endpoint:")
    test_health_endpoint()
    
    print("\n2. Testing Webhook Endpoint:")
    test_webhook_endpoint()
    
    print("\n" + "=" * 50)
    print("Test completed!")
    print("\nTo test with your Telegram bot:")
    print("1. Set up your .env file with real tokens")
    print("2. Start the bot: python main.py")
    print("3. Send /start command to your bot")
    print("4. Run this test script again")