# Free Python Server Deployment Options

Since Railway now requires a paid plan, here are the best free alternatives for deploying your Python server.

## 🎯 **Recommended: Render (Free Tier)**

### **Step 1: Create Render Account**
1. Go to [Render.com](https://render.com/)
2. Sign up with your GitHub account
3. Create a new account (free tier available)

### **Step 2: Deploy Your Python Server**
1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository (`bluecollarbuddy`)
3. Configure the service:
   - **Name:** `whatsapp-ai-server` (or any name you prefer)
   - **Root Directory:** `scripts`
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn python_server:app --host 0.0.0.0 --port $PORT`
   - **Plan:** Free

### **Step 3: Set Environment Variables**
In your Render service settings, add:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
PYTHON_SERVER_PORT=8000
```

### **Step 4: Deploy**
1. Click **"Create Web Service"**
2. Wait for deployment (usually 2-3 minutes)
3. Copy your service URL (e.g., `https://your-app-name.onrender.com`)

### **Step 5: Update Vercel**
In your Vercel project settings, add:
```bash
PYTHON_SERVER_URL=https://your-app-name.onrender.com
USE_PYTHON_SERVER=true
```

---

## 🚀 **Alternative: Fly.io (Free Tier)**

### **Step 1: Install Fly CLI**
```bash
# Windows (PowerShell)
iwr https://fly.io/install.ps1 -useb | iex

# Or download from: https://fly.io/docs/hands-on/install-flyctl/
```

### **Step 2: Login and Setup**
```bash
fly auth login
fly auth signup  # if you don't have an account
```

### **Step 3: Deploy**
```bash
cd scripts
fly launch
# Follow the prompts:
# - App name: whatsapp-ai-server
# - Region: choose closest to you
# - Deploy now: Yes
```

### **Step 4: Set Environment Variables**
```bash
fly secrets set GEMINI_API_KEY=your_gemini_api_key_here
```

### **Step 5: Get Your URL**
```bash
fly info
# Copy the URL (e.g., https://whatsapp-ai-server.fly.dev)
```

---

## 🔧 **Alternative: Vercel Functions with Python**

If you want to keep everything on Vercel, you can use Vercel's Python runtime:

### **Step 1: Create Python Function**
Create `api/python-process/route.py`:
```python
from http.server import BaseHTTPRequestHandler
import json
import os
import sys

# Add the scripts directory to Python path
sys.path.append('./scripts')

from gemini_message_processor import GeminiMessageProcessor

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))
        
        message = data.get('message', '')
        phone_number = data.get('phone_number', '')
        
        # Set environment variables
        os.environ['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY', '')
        
        # Process message
        processor = GeminiMessageProcessor()
        result = processor.process_message(message, phone_number)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode())
```

### **Step 2: Update Environment Variables**
In Vercel, set:
```bash
USE_VERCEL_PYTHON=true
GEMINI_API_KEY=your_key_here
```

---

## 🧪 **Testing Your Deployment**

### **Test Health Endpoint**
```bash
# Replace with your actual URL
curl https://your-app-name.onrender.com/health
```

### **Test Message Processing**
```bash
curl -X POST https://your-app-name.onrender.com/process-message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "phone_number": "whatsapp:+1234567890"}'
```

### **Test WhatsApp Integration**
1. Send a message to your Twilio WhatsApp sandbox
2. Check if you get intelligent responses from Bob
3. Verify the conversation flows naturally

---

## 📊 **Comparison of Free Options**

| Platform | Free Tier | Pros | Cons |
|----------|-----------|------|------|
| **Render** | 750 hours/month | Easy setup, good docs | Sleeps after inactivity |
| **Fly.io** | 3 shared VMs | Fast, global | More complex setup |
| **Vercel Functions** | 100GB-hours | Everything in one place | Limited Python support |

---

## 🎯 **My Recommendation**

**Use Render** because:
- ✅ Easiest setup
- ✅ Good free tier
- ✅ Reliable service
- ✅ Good documentation

---

## ⚠️ **Important Notes**

### **Render Free Tier Limitations:**
- Service sleeps after 15 minutes of inactivity
- First request after sleep takes 30-60 seconds
- 750 hours/month (enough for most use cases)

### **To Keep Render Service Awake:**
You can use a free service like UptimeRobot to ping your health endpoint every 10 minutes.

---

## 🔄 **Update Process**

When you make changes to your Python code:

1. **Commit to your `pol` branch:**
   ```bash
   git add .
   git commit -m "Update Python server"
   git push origin pol
   ```

2. **Render will automatically redeploy** (if connected to GitHub)

3. **Update Vercel** (if needed):
   ```bash
   vercel --prod
   ```

---

## 🎉 **Success Indicators**

✅ Python server responds to health check  
✅ Message processing returns AI responses  
✅ WhatsApp receives intelligent responses from Bob  
✅ No more generic fallback messages  

Your WhatsApp agent will now use Gemini AI for intelligent conversations! 🚀 