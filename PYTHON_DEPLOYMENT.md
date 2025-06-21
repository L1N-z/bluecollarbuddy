# Python Server Deployment Guide

This guide will help you deploy the Python server to Railway so your WhatsApp agent can use Gemini AI.

## 🚀 **Deploy to Railway (Recommended)**

### **Step 1: Create Railway Account**
1. Go to [Railway.app](https://railway.app/)
2. Sign up with your GitHub account
3. Create a new project

### **Step 2: Connect Your Repository**
1. In Railway dashboard, click **"Deploy from GitHub repo"**
2. Select your `bluecollarbuddy` repository
3. Set the **Root Directory** to: `scripts`
4. Click **"Deploy"**

### **Step 3: Configure Environment Variables**
In your Railway project settings, add these environment variables:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
PYTHON_SERVER_PORT=8000
```

### **Step 4: Get Your Server URL**
1. After deployment, Railway will give you a URL like:
   `https://your-app-name.railway.app`
2. Copy this URL - you'll need it for the next step

### **Step 5: Update Vercel Environment Variables**
In your Vercel project settings, add/update:

```bash
PYTHON_SERVER_URL=https://your-app-name.railway.app
USE_PYTHON_SERVER=true
```

### **Step 6: Test the Deployment**
1. Visit `https://your-app-name.railway.app/health`
2. You should see: `{"status": "healthy", "service": "WhatsApp AI Processor"}`

## 🔧 **Alternative: Deploy to Render**

### **Step 1: Create Render Account**
1. Go to [Render.com](https://render.com/)
2. Sign up with your GitHub account

### **Step 2: Create Web Service**
1. Click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Set **Root Directory** to: `scripts`
4. Set **Build Command** to: `pip install -r requirements.txt`
5. Set **Start Command** to: `uvicorn python_server:app --host 0.0.0.0 --port $PORT`

### **Step 3: Configure Environment**
Add environment variables:
- `GEMINI_API_KEY`
- `PYTHON_SERVER_PORT=8000`

## 🧪 **Testing Your Deployment**

### **Test Python Server**
```bash
# Test health endpoint
curl https://your-app-name.railway.app/health

# Test message processing
curl -X POST https://your-app-name.railway.app/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "phone_number": "whatsapp:+1234567890"}'
```

### **Test Full Integration**
1. Send a message to your Twilio WhatsApp sandbox
2. Check Vercel logs to see if it calls the Python server
3. Check Railway logs to see if the Python server responds

## 📊 **Monitoring**

### **Railway Logs**
- Go to your Railway project
- Click on the deployment
- Check the logs for any errors

### **Vercel Logs**
- Go to your Vercel dashboard
- Check function logs for webhook requests

## 🔄 **Update Process**

When you make changes to the Python code:

1. **Commit to your `pol` branch:**
   ```bash
   git add .
   git commit -m "Update Python server"
   git push origin pol
   ```

2. **Railway will automatically redeploy** (if connected to GitHub)

3. **Update Vercel** (if needed):
   ```bash
   vercel --prod
   ```

## 🎯 **Expected Flow After Deployment**

```
WhatsApp → Twilio → Vercel Webhook → Python Server (Railway) → Gemini AI → Response → WhatsApp
```

## ⚠️ **Troubleshooting**

### **Common Issues:**

1. **"Python server error"**
   - Check Railway logs
   - Verify `GEMINI_API_KEY` is set
   - Check if the server is running

2. **"Health check failed"**
   - Visit the health endpoint directly
   - Check Railway deployment status

3. **"Connection refused"**
   - Verify the `PYTHON_SERVER_URL` in Vercel
   - Check if Railway service is running

### **Debug Commands:**
```bash
# Check if Python server is responding
curl https://your-app-name.railway.app/health

# Test message processing
curl -X POST https://your-app-name.railway.app/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "test", "phone_number": "test"}'
```

## 🎉 **Success Indicators**

✅ Python server responds to health check  
✅ Message processing returns AI responses  
✅ WhatsApp receives intelligent responses from Bob  
✅ No more generic fallback messages  

Your WhatsApp agent will now use Gemini AI for intelligent conversations! 🚀 