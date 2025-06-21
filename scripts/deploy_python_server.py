#!/usr/bin/env python3
"""
Deployment script for the Python WhatsApp AI server
Supports deployment to Railway, Render, and other platforms
"""

import os
import sys
import subprocess
from pathlib import Path

def create_procfile():
    """Create Procfile for Railway/Render deployment"""
    procfile_content = """web: uvicorn python_server:app --host 0.0.0.0 --port $PORT
"""
    
    procfile_path = Path(__file__).parent / "Procfile"
    with open(procfile_path, "w") as f:
        f.write(procfile_content)
    
    print("✅ Created Procfile for deployment")

def create_runtime_txt():
    """Create runtime.txt for Python version specification"""
    runtime_content = "python-3.11.0\n"
    
    runtime_path = Path(__file__).parent / "runtime.txt"
    with open(runtime_path, "w") as f:
        f.write(runtime_content)
    
    print("✅ Created runtime.txt")

def create_railway_json():
    """Create railway.json for Railway deployment configuration"""
    railway_config = {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn python_server:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health",
            "healthcheckTimeout": 300,
            "restartPolicyType": "ON_FAILURE",
            "restartPolicyMaxRetries": 10
        }
    }
    
    import json
    railway_path = Path(__file__).parent / "railway.json"
    with open(railway_path, "w") as f:
        json.dump(railway_config, f, indent=2)
    
    print("✅ Created railway.json")

def create_dockerfile():
    """Create Dockerfile for containerized deployment"""
    dockerfile_content = """FROM python:3.11-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "python_server:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    dockerfile_path = Path(__file__).parent / "Dockerfile"
    with open(dockerfile_path, "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Created Dockerfile")

def create_docker_compose():
    """Create docker-compose.yml for local development"""
    compose_content = """version: '3.8'

services:
  whatsapp-ai-server:
    build: .
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=${GEMINI_API_KEY}
      - PYTHON_SERVER_PORT=8000
    volumes:
      - .:/app
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
"""
    
    compose_path = Path(__file__).parent / "docker-compose.yml"
    with open(compose_path, "w") as f:
        f.write(compose_content)
    
    print("✅ Created docker-compose.yml")

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nThese will need to be set in your deployment platform.")
        return False
    
    print("✅ Environment variables check passed")
    return True

def main():
    """Main deployment setup function"""
    print("🚀 WhatsApp AI Server - Deployment Setup")
    print("=" * 50)
    
    # Check environment
    check_environment()
    
    print("\n📦 Creating deployment files...")
    
    # Create deployment files
    create_procfile()
    create_runtime_txt()
    create_railway_json()
    create_dockerfile()
    create_docker_compose()
    
    print("\n✅ Deployment files created successfully!")
    print("\n📋 Deployment Options:")
    print("\n1. Railway (Recommended):")
    print("   - Connect your GitHub repo to Railway")
    print("   - Set root directory to 'scripts/'")
    print("   - Add environment variables:")
    print("     - GEMINI_API_KEY")
    print("   - Deploy automatically")
    
    print("\n2. Render:")
    print("   - Create new Web Service")
    print("   - Connect your GitHub repo")
    print("   - Set build command: pip install -r requirements.txt")
    print("   - Set start command: uvicorn python_server:app --host 0.0.0.0 --port $PORT")
    print("   - Add environment variables")
    
    print("\n3. Docker:")
    print("   - Build: docker build -t whatsapp-ai-server .")
    print("   - Run: docker run -p 8000:8000 -e GEMINI_API_KEY=your_key whatsapp-ai-server")
    
    print("\n4. Local with Docker Compose:")
    print("   - Run: docker-compose up --build")
    
    print("\n🔗 After deployment:")
    print("1. Get your server URL (e.g., https://your-app.railway.app)")
    print("2. Update your Vercel environment variable:")
    print("   PYTHON_SERVER_URL=https://your-app.railway.app")
    print("3. Test the health endpoint: https://your-app.railway.app/health")
    
    print("\n🎯 Next Steps:")
    print("1. Choose your deployment platform")
    print("2. Follow the platform-specific instructions above")
    print("3. Update your Vercel environment variables")
    print("4. Test the integration")

if __name__ == "__main__":
    main() 