#!/usr/bin/env python3
"""
Startup script for the WhatsApp AI Agent
This script starts the Python FastAPI server and provides instructions for the Next.js app
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ['GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables before starting the servers.")
        return False
    
    print("✅ Environment variables check passed")
    return True

def install_python_dependencies():
    """Install Python dependencies if needed"""
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def start_python_server():
    """Start the Python FastAPI server"""
    server_file = Path(__file__).parent / "python_server.py"
    
    if not server_file.exists():
        print("❌ python_server.py not found")
        return False
    
    print("🚀 Starting Python FastAPI server...")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation: http://localhost:8000/docs")
    print("   Health Check: http://localhost:8000/health")
    print()
    
    try:
        # Change to the scripts directory
        os.chdir(Path(__file__).parent)
        
        # Start the server
        subprocess.run([
            sys.executable, "python_server.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Python server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start Python server: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🤖 WhatsApp AI Agent - Server Startup")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Install dependencies
    if not install_python_dependencies():
        sys.exit(1)
    
    print("\n📋 Next Steps:")
    print("1. In a new terminal, start the Next.js app:")
    print("   cd /path/to/your/project")
    print("   npm install")
    print("   npm run dev")
    print()
    print("2. The Next.js app will be available at: http://localhost:3000")
    print("3. The Python server will be available at: http://localhost:8000")
    print()
    print("4. Configure your Twilio webhook URL to:")
    print("   https://your-vercel-domain.vercel.app/api/webhook")
    print()
    print("5. Set the environment variable in your Next.js app:")
    print("   PYTHON_SERVER_URL=http://localhost:8000")
    print()
    
    # Start Python server
    start_python_server()

if __name__ == "__main__":
    main() 