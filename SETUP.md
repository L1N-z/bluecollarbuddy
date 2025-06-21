# WhatsApp AI Agent Setup Guide

This guide will help you set up the WhatsApp AI agent that integrates Twilio, Gemini AI, and your Python backend.

## 🏗️ Architecture Overview

```
WhatsApp User → Twilio Sandbox → Vercel Webhook → Python AI Processor → Gemini AI → Response → WhatsApp User
```

## 📋 Prerequisites

1. **Twilio Account** with WhatsApp Sandbox enabled
2. **Google AI Studio** account with Gemini API key
3. **Vercel** account for deployment
4. **Python 3.8+** installed locally
5. **Node.js 18+** installed locally

## 🔧 Environment Variables

### For Vercel Deployment (Next.js App)

Add these environment variables in your Vercel project settings:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890

# Google AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# App Configuration
NEXT_PUBLIC_BASE_URL=https://your-vercel-domain.vercel.app
PYTHON_SERVER_URL=https://your-python-server-domain.com
```

### For Local Development

Create a `.env.local` file in your project root:

```bash
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=whatsapp:+1234567890

# Google AI Configuration
GEMINI_API_KEY=your_gemini_api_key

# App Configuration
NEXT_PUBLIC_BASE_URL=http://localhost:3000
PYTHON_SERVER_URL=http://localhost:8000
```

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
# Install Next.js dependencies
npm install

# Install Python dependencies
cd scripts
pip install -r requirements.txt
```

### Step 2: Configure Twilio WhatsApp Sandbox

1. Go to your [Twilio Console](https://console.twilio.com/)
2. Navigate to **Messaging** → **Try it out** → **Send a WhatsApp message**
3. In the **When a message comes in** field, set:
   ```
   https://your-vercel-domain.vercel.app/api/webhook
   ```
4. Leave the **Status callback URL** field empty for now
5. Save the configuration

### Step 3: Start the Servers

#### Option A: Using the Startup Script (Recommended)

```bash
cd scripts
python start_servers.py
```

This will:
- Check environment variables
- Install Python dependencies
- Start the Python FastAPI server
- Provide instructions for starting the Next.js app

#### Option B: Manual Startup

**Terminal 1 - Python Server:**
```bash
cd scripts
python python_server.py
```

**Terminal 2 - Next.js App:**
```bash
npm run dev
```

### Step 4: Test the Integration

1. **Test Python Server:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Test Message Processing:**
   ```bash
   curl -X POST http://localhost:8000/process-message \
     -H "Content-Type: application/json" \
     -d '{"message": "Hello", "phone_number": "whatsapp:+1234567890"}'
   ```

3. **Test WhatsApp Integration:**
   - Send a message to your Twilio WhatsApp sandbox number
   - Check the logs in both terminals for processing details

## 🌐 Deployment Options

### Option 1: Vercel + Railway (Recommended)

1. **Deploy Next.js to Vercel:**
   ```bash
   vercel --prod
   ```

2. **Deploy Python Server to Railway:**
   - Connect your GitHub repo to Railway
   - Set the root directory to `scripts/`
   - Add environment variables
   - Deploy

3. **Update Environment Variables:**
   - Set `PYTHON_SERVER_URL` to your Railway app URL
   - Update Twilio webhook URL to your Vercel domain

### Option 2: Vercel + Vercel Functions

For a simpler setup, you can modify the code to run the Python logic directly in Vercel functions (requires additional setup).

## 🔍 Troubleshooting

### Common Issues

1. **"GEMINI_API_KEY not configured"**
   - Ensure the environment variable is set correctly
   - Check that the API key is valid in Google AI Studio

2. **"Twilio send error"**
   - Verify your Twilio credentials
   - Check that your WhatsApp sandbox is active
   - Ensure the phone number format is correct (whatsapp:+1234567890)

3. **"Python server error"**
   - Check that the Python server is running on port 8000
   - Verify the `PYTHON_SERVER_URL` environment variable
   - Check Python server logs for errors

4. **Webhook not receiving messages**
   - Verify the webhook URL in Twilio console
   - Check that your Vercel deployment is live
   - Ensure the webhook endpoint is accessible

### Debug Mode

Enable debug logging by setting:
```bash
DEBUG=true
```

This will show detailed logs in both the Next.js and Python servers.

## 📊 Monitoring

### Logs to Monitor

1. **Vercel Function Logs:**
   - Go to your Vercel dashboard
   - Check function logs for webhook requests

2. **Python Server Logs:**
   - Check the terminal running the Python server
   - Look for processing and error messages

3. **Twilio Console:**
   - Monitor message delivery status
   - Check for any webhook failures

## 🔄 Message Flow

1. **User sends message** → WhatsApp mobile app
2. **Twilio receives message** → WhatsApp sandbox
3. **Twilio calls webhook** → `https://your-domain.vercel.app/api/webhook`
4. **Webhook processes message** → Calls `/api/process-message`
5. **Process message calls Python** → `http://localhost:8000/process-message`
6. **Python calls Gemini AI** → Processes with Bob's persona
7. **Response flows back** → Python → Next.js → Twilio → WhatsApp → User

## 🎯 Next Steps

1. **Customize Bob's Persona:** Edit the persona in `scripts/gemini_message_processor.py`
2. **Add Database Integration:** Implement conversation history storage
3. **Add Analytics:** Track message volume and user engagement
4. **Scale Up:** Move to production Twilio WhatsApp Business API
5. **Add Features:** Media handling, quick replies, etc.

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Review the logs in both servers
3. Verify all environment variables are set correctly
4. Test each component individually

The system is designed to be robust with fallbacks, so even if one component fails, users will receive helpful error messages. 