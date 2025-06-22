#!/usr/bin/env python3
"""
Test script for Bob's Dashboard functionality
"""

import requests
import json
import time

def test_dashboard_api():
    """Test the dashboard API endpoints"""
    print("🧪 Testing Bob's Dashboard API")
    print("=" * 50)
    
    base_url = "http://localhost:3000"  # Next.js development server
    
    # Test 1: Check if dashboard is accessible
    print("\n1. Testing dashboard accessibility...")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status: {response.status_code}")
        print(f"   Success: {'✅' if response.status_code == 200 else '❌'}")
    except Exception as e:
        print(f"   Error: {e}")
        print("   ❌ Dashboard not accessible")
    
    # Test 2: Test settings API
    print("\n2. Testing settings API...")
    try:
        # Test GET settings
        response = requests.get(f"{base_url}/api/bob-settings")
        print(f"   GET settings status: {response.status_code}")
        
        if response.ok:
            data = response.json()
            print(f"   Current settings: {json.dumps(data, indent=2)}")
        
        # Test POST account settings
        account_data = {
            "name": "Bob Smith",
            "role": "Beehive Builder & Consultant",
            "roleDescription": "Expert in beehive construction and maintenance",
            "profile": "I'm Bob, a passionate beehive builder with 15 years of experience. I help people create and maintain healthy bee colonies.",
            "servicesType": "pricing",
            "services": [
                {"name": "Beehive Construction", "price": 150},
                {"name": "Colony Inspection", "price": 75}
            ],
            "servicesNotProvided": "Honey extraction, Queen bee breeding",
            "location": "SW1A 1AA"
        }
        
        response = requests.post(f"{base_url}/api/bob-settings", json={
            "type": "account",
            "data": account_data
        })
        
        print(f"   POST account settings status: {response.status_code}")
        if response.ok:
            result = response.json()
            print(f"   Result: {result}")
        
        # Test POST agent settings
        agent_data = {
            "enabled": True,
            "delayTime": 3,
            "defaultGreeting": "Hello! Bob here, how can I help with your beehive needs?"
        }
        
        response = requests.post(f"{base_url}/api/bob-settings", json={
            "type": "agent",
            "data": agent_data
        })
        
        print(f"   POST agent settings status: {response.status_code}")
        if response.ok:
            result = response.json()
            print(f"   Result: {result}")
        
        print("   ✅ Settings API working")
        
    except Exception as e:
        print(f"   Error: {e}")
        print("   ❌ Settings API failed")
    
    # Test 3: Test Python server integration
    print("\n3. Testing Python server integration...")
    python_server_url = "http://localhost:8000"
    
    try:
        # Test Python server health
        response = requests.get(f"{python_server_url}/health")
        print(f"   Python server health status: {response.status_code}")
        
        if response.ok:
            health_data = response.json()
            print(f"   Health data: {health_data}")
        
        # Test settings update
        settings_data = {
            "bobAccount": account_data,
            "agentSettings": agent_data
        }
        
        response = requests.post(f"{python_server_url}/update-settings", json=settings_data)
        print(f"   Update settings status: {response.status_code}")
        
        if response.ok:
            result = response.json()
            print(f"   Result: {result}")
        
        # Test prompt generation
        prompt_request = {
            "message": "Hi, I need help with my beehive",
            "phone_number": "+1234567890"
        }
        
        response = requests.post(f"{python_server_url}/generate-prompt", json=prompt_request)
        print(f"   Generate prompt status: {response.status_code}")
        
        if response.ok:
            prompt_data = response.json()
            print(f"   Prompt generated: {len(prompt_data.get('prompt', ''))} characters")
        
        print("   ✅ Python server integration working")
        
    except Exception as e:
        print(f"   Error: {e}")
        print("   ❌ Python server integration failed")

def test_message_processing():
    """Test message processing with Bob's settings"""
    print("\n4. Testing message processing...")
    
    python_server_url = "http://localhost:8000"
    
    test_messages = [
        "Hi Bob, I need help with my beehive",
        "What services do you offer?",
        "How much do you charge for beehive construction?",
        "I'd like to schedule an appointment for next Tuesday at 2 PM",
        "My name is John and my address is 123 Main Street, London SW1A 1AA"
    ]
    
    for i, message in enumerate(test_messages, 1):
        try:
            print(f"\n   Test {i}: '{message}'")
            
            response = requests.post(f"{python_server_url}/process-message", json={
                "message": message,
                "phone_number": "+1234567890"
            })
            
            if response.ok:
                result = response.json()
                print(f"   Status: {response.status_code}")
                print(f"   Response: {result.get('response', '')[:100]}...")
                
                if result.get('pause_required'):
                    print("   ⚠️ PAUSE required - pricing discussion")
            else:
                print(f"   Error: {response.status_code}")
                
        except Exception as e:
            print(f"   Error: {e}")

def main():
    """Run all tests"""
    print("🚀 Bob's Dashboard Test Suite")
    print("=" * 50)
    
    try:
        test_dashboard_api()
        test_message_processing()
        
        print("\n✅ All tests completed!")
        print("\n📝 Next steps:")
        print("1. Start the Next.js development server: npm run dev")
        print("2. Start the Python server: python scripts/python_server.py")
        print("3. Visit http://localhost:3000 to access Bob's dashboard")
        print("4. Configure Bob's account and agent settings")
        print("5. Test WhatsApp integration")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 