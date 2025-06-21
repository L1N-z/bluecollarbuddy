#!/usr/bin/env python3
"""
Integration test script for the WhatsApp AI agent
Tests the complete flow from message processing to response generation
"""

import os
import sys
import requests
import json
from pathlib import Path

def test_python_server():
    """Test the Python FastAPI server"""
    print("🧪 Testing Python Server...")
    
    base_url = os.getenv("PYTHON_SERVER_URL", "http://localhost:8000")
    
    # Test health endpoint
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Health check passed")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Health check failed: {e}")
        return False
    
    # Test message processing
    test_messages = [
        ("Hello!", "whatsapp:+1234567890"),
        ("I need help with building a beehive", "whatsapp:+1234567890"),
        ("What types of hives do you recommend?", "whatsapp:+1234567890"),
    ]
    
    for message, phone in test_messages:
        try:
            response = requests.post(
                f"{base_url}/process-message",
                json={"message": message, "phone_number": phone},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Message processed: '{message}' → '{result['response'][:50]}...'")
            else:
                print(f"❌ Message processing failed: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Message processing failed: {e}")
            return False
    
    print("✅ Python server tests passed")
    return True

def test_nextjs_endpoints():
    """Test the Next.js API endpoints"""
    print("\n🧪 Testing Next.js Endpoints...")
    
    base_url = os.getenv("NEXT_PUBLIC_BASE_URL", "http://localhost:3000")
    
    # Test process-message endpoint
    try:
        response = requests.post(
            f"{base_url}/api/process-message",
            json={"message": "Hello!", "from": "whatsapp:+1234567890"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Next.js endpoint working: '{result['response'][:50]}...'")
        else:
            print(f"❌ Next.js endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Next.js endpoint failed: {e}")
        return False
    
    print("✅ Next.js endpoints tests passed")
    return True

def test_environment():
    """Test environment variables"""
    print("\n🧪 Testing Environment Variables...")
    
    required_vars = [
        "GEMINI_API_KEY",
        "TWILIO_ACCOUNT_SID", 
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
        else:
            print(f"✅ {var} is set")
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    print("✅ Environment variables check passed")
    return True

def test_gemini_connection():
    """Test Gemini API connection"""
    print("\n🧪 Testing Gemini API Connection...")
    
    try:
        from gemini_message_processor import GeminiMessageProcessor
        
        processor = GeminiMessageProcessor()
        result = processor.process_message("Hello", "whatsapp:+1234567890")
        
        if result and result.get('response'):
            print(f"✅ Gemini API working: '{result['response'][:50]}...'")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 WhatsApp AI Agent - Integration Test")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment),
        ("Gemini API Connection", test_gemini_connection),
        ("Python Server", test_python_server),
        ("Next.js Endpoints", test_nextjs_endpoints),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your WhatsApp AI agent is ready to use.")
        print("\n📋 Next Steps:")
        print("1. Deploy your Next.js app to Vercel")
        print("2. Deploy your Python server to Railway/Render")
        print("3. Update environment variables in Vercel")
        print("4. Configure Twilio webhook URL")
        print("5. Test with a real WhatsApp message")
    else:
        print("⚠️  Some tests failed. Please check the errors above and fix them.")
        print("\n🔧 Common fixes:")
        print("- Ensure all environment variables are set")
        print("- Make sure the Python server is running on port 8000")
        print("- Make sure the Next.js app is running on port 3000")
        print("- Check your Gemini API key is valid")
        print("- Verify your Twilio credentials")

if __name__ == "__main__":
    main() 