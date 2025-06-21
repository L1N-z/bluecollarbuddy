# Quick Start Guide - Two Options

You have **two ways** to run your Python scripts. Choose the one that fits your needs:

## 🚀 Option 1: Direct Python Scripts (Simpler - Development)

**No separate backend server needed!** Your Python scripts run directly from the Next.js app.

### Setup:
```bash
# 1. Install dependencies
npm install
cd scripts
pip install -r requirements.txt

# 2. Set environment variables in .env.local
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
NEXT_PUBLIC_BASE_URL=http://localhost:3000
USE_PYTHON_SERVER=false  # This enables direct script execution

# 3. Start the app
npm run dev
```

### How it works:
- ✅ Next.js calls your Python script directly using `child_process`
- ✅ No separate server to manage
- ✅ Perfect for development and testing
- ✅ Works with your existing `gemini_message_processor.py`

### Pros:
- Simple setup
- No additional deployment needed
- Good for development and small-scale use

### Cons:
- Slower for multiple requests
- Less scalable
- Not ideal for production with high traffic

---

## 🌐 Option 2: Separate Python Server (Production-Ready)

**Recommended for production.** Runs your Python scripts as a separate FastAPI server.

### Setup:
```bash
# 1. Install dependencies
npm install
cd scripts
pip install -r requirements.txt

# 2. Set environment variables in .env.local
GEMINI_API_KEY=your_gemini_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890
NEXT_PUBLIC_BASE_URL=http://localhost:3000
PYTHON_SERVER_URL=http://localhost:8000
USE_PYTHON_SERVER=true  # This enables server mode

# 3. Start both servers
# Terminal 1 - Python server
cd scripts
python python_server.py

# Terminal 2 - Next.js app
npm run dev
```

### How it works:
- ✅ Python FastAPI server wraps your `GeminiMessageProcessor`
- ✅ Next.js makes HTTP requests to the Python server
- ✅ Better performance and scalability
- ✅ Can handle multiple requests simultaneously

### Pros:
- Better performance
- More scalable
- Production-ready
- Can add database, caching, etc.

### Cons:
- Requires managing two services
- More complex initial setup

---

## 🎯 Which Option Should You Choose?

### Choose **Option 1 (Direct Scripts)** if:
- You're just getting started
- You want to test quickly
- You have low traffic
- You prefer simplicity

### Choose **Option 2 (Separate Server)** if:
- You're planning for production
- You expect high traffic
- You want better performance
- You plan to add more features

---

## 🔧 Switching Between Options

You can easily switch between the two approaches by changing one environment variable:

```bash
# For direct scripts (Option 1)
USE_PYTHON_SERVER=false

# For separate server (Option 2)  
USE_PYTHON_SERVER=true
```

---

## 🧪 Testing Your Setup

Run the integration test to verify everything works:

```bash
cd scripts
python test_integration.py
```

---

## 📱 Twilio Configuration

For both options, configure your Twilio webhook:

1. Go to [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. Set **When a message comes in** to: `https://your-vercel-domain.vercel.app/api/webhook`
4. Leave **Status callback URL** empty
5. Save the configuration

---

## 🚀 Deployment

### For Option 1 (Direct Scripts):
- Deploy to Vercel normally
- Make sure Python dependencies are available (Vercel supports Python)

### For Option 2 (Separate Server):
- Deploy Next.js to Vercel
- Deploy Python server to Railway/Render
- Update `PYTHON_SERVER_URL` in Vercel environment variables

---

## 💡 Pro Tip

Start with **Option 1** for development and testing, then switch to **Option 2** when you're ready for production. The code automatically handles both approaches! 