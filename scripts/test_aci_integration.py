#!/usr/bin/env python3
"""
Test script for ACI Calendar Integration
This script tests the calendar agents and appointment scheduling functionality
"""

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aci_calendar_agents import AciCalendarAgents
from gemini_calendar_processor import GeminiCalendarProcessor

def test_aci_connection():
    """Test basic ACI connection"""
    print("🔍 Testing ACI Connection...")
    
    try:
        agents = AciCalendarAgents()
        print("✅ ACI Calendar Agents initialized successfully")
        return True
    except Exception as e:
        print(f"❌ ACI Connection failed: {e}")
        return False

def test_calendar_reader():
    """Test calendar reader functionality"""
    print("\n📅 Testing Calendar Reader...")
    
    try:
        agents = AciCalendarAgents()
        
        # Test with today's date
        today = datetime.now().strftime("%Y-%m-%d")
        result = agents.get_calendar_events(today, "test_phone")
        
        print(f"📅 Calendar Reader Result: {json.dumps(result, indent=2)}")
        
        if result['success']:
            print("✅ Calendar Reader working")
            return True
        else:
            print(f"❌ Calendar Reader failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Calendar Reader test failed: {e}")
        return False

def test_appointment_extraction():
    """Test appointment details extraction"""
    print("\n🔍 Testing Appointment Details Extraction...")
    
    try:
        agents = AciCalendarAgents()
        
        test_messages = [
            "Can we meet on 2025-01-22 at 2:00 PM at my house?",
            "I want to schedule for tomorrow at 3 PM",
            "How about next week at 10 AM in your office?",
            "Just checking my calendar for today"
        ]
        
        for i, message in enumerate(test_messages, 1):
            details = agents.extract_appointment_details(message)
            print(f"📝 Test {i}: {message}")
            print(f"   Extracted: {json.dumps(details, indent=4)}")
            print()
        
        print("✅ Appointment extraction working")
        return True
        
    except Exception as e:
        print(f"❌ Appointment extraction test failed: {e}")
        return False

def test_availability_check():
    """Test availability checking"""
    print("\n⏰ Testing Availability Check...")
    
    try:
        agents = AciCalendarAgents()
        
        # Test with tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = agents.check_availability_and_propose(tomorrow, "test_phone")
        
        print(f"⏰ Availability Result: {json.dumps(result, indent=2)}")
        
        if 'available' in result:
            print("✅ Availability check working")
            return True
        else:
            print(f"❌ Availability check failed: {result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Availability check test failed: {e}")
        return False

def test_gemini_calendar_processor():
    """Test Gemini calendar processor"""
    print("\n🤖 Testing Gemini Calendar Processor...")
    
    try:
        processor = GeminiCalendarProcessor()
        
        test_message = "Hi Bob, I'd like to schedule a consultation for tomorrow at 2 PM at my house"
        result = processor.process_message(test_message, "test_phone")
        
        print(f"🤖 Gemini Processor Result: {json.dumps(result, indent=2)}")
        
        if result.get('success'):
            print("✅ Gemini Calendar Processor working")
            return True
        else:
            print(f"❌ Gemini Processor failed: {result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Gemini Processor test failed: {e}")
        return False

def test_python_server_endpoints():
    """Test Python server endpoints"""
    print("\n🌐 Testing Python Server Endpoints...")
    
    server_url = os.getenv('PYTHON_SERVER_URL', 'http://localhost:8000')
    
    endpoints_to_test = [
        ('GET', '/health', None),
        ('GET', '/', None),
        ('POST', '/calendar/events', {
            'date': datetime.now().strftime("%Y-%m-%d"),
            'phone_number': 'test_phone'
        }),
        ('POST', '/process-appointment', {
            'message': 'Hi Bob, I want to schedule a consultation',
            'phone_number': 'test_phone'
        })
    ]
    
    for method, endpoint, data in endpoints_to_test:
        try:
            url = f"{server_url}{endpoint}"
            print(f"🌐 Testing {method} {endpoint}...")
            
            if method == 'GET':
                response = requests.get(url, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {endpoint} working")
                if data:
                    print(f"   Response: {json.dumps(response.json(), indent=2)}")
            else:
                print(f"❌ {endpoint} failed: {response.status_code}")
                print(f"   Response: {response.text}")
                
        except Exception as e:
            print(f"❌ {endpoint} test failed: {e}")
    
    return True

def test_environment_variables():
    """Test environment variables"""
    print("\n🔧 Testing Environment Variables...")
    
    required_vars = [
        'ACI_API_KEY',
        'LINKED_ACCOUNT_OWNER_ID',
        'GEMINI_API_KEY',
        'PYTHON_SERVER_URL'
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
    print("🚀 Starting ACI Calendar Integration Tests")
    print("=" * 50)
    
    tests = [
        ("Environment Variables", test_environment_variables),
        ("ACI Connection", test_aci_connection),
        ("Calendar Reader", test_calendar_reader),
        ("Appointment Extraction", test_appointment_extraction),
        ("Availability Check", test_availability_check),
        ("Gemini Calendar Processor", test_gemini_calendar_processor),
        ("Python Server Endpoints", test_python_server_endpoints)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! ACI integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print("\n💡 Next steps:")
        print("1. Check environment variables")
        print("2. Verify ACI.dev account setup")
        print("3. Ensure calendar app is configured")
        print("4. Check Python server is running")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 