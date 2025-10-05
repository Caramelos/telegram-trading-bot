# 🚀 **RAILWAY DEPLOYMENT GUIDE**

## **STEP-BY-STEP RAILWAY DEPLOYMENT**

### **STEP 1: Sign Up for Railway (2 minutes)**

1. **Go to**: https://railway.app
2. **Click "Login"** 
3. **Sign up with GitHub** (recommended)
4. **Verify your account**

### **STEP 2: Create New Project**

1. **Click "New Project"**
2. **Select "Deploy from GitHub repo"**
3. **If you don't have GitHub repo, select "Empty Project"**

### **STEP 3: Upload Your Files**

You need to upload these files from `/Users/shuang/Desktop/telegram-trading-bot/`:

**Essential Files:**
- `webhook_server_standalone.py` ✅
- `config.py` ✅
- `requirements.txt` ✅ 
- `.env.example` ✅
- `Procfile` ✅
- `runtime.txt` ✅

**Method A: GitHub (Recommended)**
1. Create GitHub repository
2. Upload all files
3. Connect Railway to GitHub

**Method B: Direct Upload**
1. Drag and drop files to Railway
2. Or use Railway CLI

### **STEP 4: Set Environment Variables**

In Railway dashboard, go to **Variables** and add:

```
BOT_TOKEN=8357026148:AAHoQhclTPy1L2Q7DYcdxwjWtrdeqBlSyOA
WEBHOOK_SECRET=tradepods_secret_2025
ALLOWED_CHAT_IDS=5101999928
ALLOWED_TOKENS=BTCUSD,ETHUSD,ADAUSD,SOLUSD
ALLOWED_STRATEGIES=EMA_Cross,RSI_Divergence,MACD_Signal
```

### **STEP 5: Deploy**

1. **Click "Deploy"**
2. **Wait for build to complete** (2-3 minutes)
3. **Get your webhook URL**: `https://your-app.railway.app`

### **STEP 6: Test Your Deployment**

**Your webhook URL will be:**
`https://your-app.railway.app/webhook`

**Test endpoints:**
- `https://your-app.railway.app/health` - Health check
- `https://your-app.railway.app/test` - Test signal  

### **STEP 7: Connect to TradingView**

In your TradingView alerts:
- **Webhook URL**: `https://your-app.railway.app/webhook`
- **Message**: 
```json
{"secret":"tradepods_secret_2025","action":"{{strategy.order.action}}","symbol":"{{ticker}}","price":"{{close}}","strategy":"Your Strategy Name","exchange":"{{exchange}}","message":"{{strategy.order.comment}}","timestamp":"{{time}}"}
```

## **🎯 NEXT STEPS**

1. **Complete Railway signup**
2. **Create project and upload files**
3. **Set environment variables**
4. **Deploy and get webhook URL**
5. **Test the webhook**
6. **Connect to TradingView**

## **📞 SUPPORT**

If you need help:
1. **Railway Documentation**: https://docs.railway.app
2. **Railway Discord**: https://discord.gg/railway

---

**Ready to start? Go to https://railway.app and let me know when you've signed up!**