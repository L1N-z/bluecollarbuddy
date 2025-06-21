#!/usr/bin/env python3
"""
Test script for appointment extraction and scheduling flow
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aci_calendar_agents import AciCalendarAgents
from gemini_calendar_processor import GeminiCalendarProcessor

def test_appointment_extraction():
    """Test appointment details extraction"""
    print("🧪 Testing Appointment Extraction")
    print("=" * 50)
    
    agents = AciCalendarAgents()
    processor = GeminiCalendarProcessor()
    
    # Test conversation flow
    test_conversation = [
        "Hello",
        "I have two beehives but they both are rather old and require maintenance. One of them has even started to rot, so I'd like to fix them up before they get worse",
        "They are top bar hives. I live 10 miles away from you",
        "Yes, next Tuesday is fine",
        "No, 2 pm wouldn't work for me. How about 4pm?",
        "Yes, sounds good"
    ]
    
    phone_number = "+1234567890"
    
    for i, message in enumerate(test_conversation, 1):
        print(f"\n📝 Message {i}: {message}")
        
        # Test extraction
        extracted = agents.extract_appointment_details(message)
        print(f"   Extracted: {extracted}")
        
        # Test processing
        result = processor.process_message(message, phone_number, [])
        print(f"   Response: {result.get('response', 'No response')}")
        print(f"   Success: {result.get('success', False)}")
        
        # Show context
        context = agents.get_appointment_context(phone_number)
        print(f"   Context: {context}")
        
        print("-" * 30)

def test_natural_language_extraction():
    """Test natural language date/time extraction"""
    print("\n🔍 Testing Natural Language Extraction")
    print("=" * 50)
    
    agents = AciCalendarAgents()
    
    test_messages = [
        "next Tuesday",
        "4pm",
        "at my house",
        "next Tuesday at 4pm at my house",
        "tomorrow morning",
        "this afternoon",
        "Yes, sounds good"
    ]
    
    for message in test_messages:
        extracted = agents.extract_appointment_details(message)
        print(f"📝 '{message}' -> {extracted}")

def test_date_conversion():
    """Test natural date conversion"""
    print("\n📅 Testing Date Conversion")
    print("=" * 50)
    
    agents = AciCalendarAgents()
    
    test_dates = [
        "next tuesday",
        "tomorrow",
        "today",
        "next monday",
        "next friday"
    ]
    
    for date_str in test_dates:
        converted = agents._convert_natural_date(date_str)
        print(f"📅 '{date_str}' -> {converted}")

if __name__ == "__main__":
    print("🚀 Starting Appointment Extraction Tests")
    print("=" * 60)
    
    test_natural_language_extraction()
    test_date_conversion()
    test_appointment_extraction()
    
    print("\n✅ Tests completed!") 