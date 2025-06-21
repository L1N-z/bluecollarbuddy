#!/usr/bin/env python3
"""
Test script for WhatsApp flow
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_python_server():
    """Test if Python server is running and accessible"""
    print("🌐 Testing Python Server")
    print("=" * 40)
    
    server_url = os.getenv('PYTHON_SERVER_URL', 'http://localhost:8000')
    
    try:
        # Test health endpoint
        health_response = requests.get(f"{server_url}/health", timeout=10)
        print(f"✅ Health check: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"   Status: {health_data.get('status')}")
            print(f"   Missing env vars: {health_data.get('missing_environment_variables', [])}")
        
        # Test API key status
        api_status_response = requests.get(f"{server_url}/api-keys/status", timeout=10)
        print(f"✅ API key status: {api_status_response.status_code}")
        if api_status_response.status_code == 200:
            api_data = api_status_response.json()
            print(f"   API Key Status: {json.dumps(api_data.get('api_key_status', {}), indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Python server test failed: {e}")
        return False

def test_message_processing():
    """Test message processing"""
    print("\n💬 Testing Message Processing")
    print("=" * 40)
    
    server_url = os.getenv('PYTHON_SERVER_URL', 'http://localhost:8000')
    
    test_messages = [
        "Hi",
        "Hello",
        "I need help with my beehive",
        "Can I schedule an appointment?"
    ]
    
    for message in test_messages:
        try:
            response = requests.post(f"{server_url}/process-message", 
                json={
                    "message": message,
                    "phone_number": "+1234567890",
                    "conversation_history": []
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ '{message}' -> {result.get('response', 'No response')}")
            else:
                print(f"❌ '{message}' -> Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ '{message}' -> Exception: {e}")

def test_appointment_processing():
    """Test appointment processing"""
    print("\n📅 Testing Appointment Processing")
    print("=" * 40)
    
    server_url = os.getenv('PYTHON_SERVER_URL', 'http://localhost:8000')
    
    test_messages = [
        "I want to schedule a consultation",
        "next Tuesday at 4pm",
        "at my house",
        "Yes, sounds good"
    ]
    
    phone_number = "+1234567890"
    
    for message in test_messages:
        try:
            response = requests.post(f"{server_url}/process-appointment", 
                json={
                    "message": message,
                    "phone_number": phone_number,
                    "conversation_history": []
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ '{message}' -> {result.get('response', 'No response')}")
            else:
                print(f"❌ '{message}' -> Error {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ '{message}' -> Exception: {e}")

def test_environment_variables():
    """Test environment variables"""
    print("\n🔧 Testing Environment Variables")
    print("=" * 40)
    
    required_vars = [
        'PYTHON_SERVER_URL',
        'GEMINI_API_KEY',
        'ACI_CALENDAR_READER_API_KEY',
        'ACI_EVENT_CREATOR_API_KEY',
        'LINKED_ACCOUNT_OWNER_ID',
        'TWILIO_ACCOUNT_SID',
        'TWILIO_AUTH_TOKEN',
        'TWILIO_PHONE_NUMBER'
    ]
    
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * len(value)} (length: {len(value)})")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {missing_vars}")
        return False
    else:
        print("\n✅ All environment variables set")
        return True

def main():
    """Run all tests"""
    print("🚀 Starting WhatsApp Flow Tests")
    print("=" * 60)
    
    # Test environment variables
    env_ok = test_environment_variables()
    
    if not env_ok:
        print("\n❌ Environment variables missing. Please set them before testing.")
        return
    
    # Test Python server
    server_ok = test_python_server()
    
    if not server_ok:
        print("\n❌ Python server not accessible. Please check if it's running.")
        return
    
    # Test message processing
    test_message_processing()
    
    # Test appointment processing
    test_appointment_processing()
    
    print("\n✅ Tests completed!")

if __name__ == "__main__":
    main() 