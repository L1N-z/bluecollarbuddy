import os
import json
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from aci_calendar_agents import AciCalendarAgents
from robust_event_creator import RobustEventCreator

class GeminiCalendarProcessor:
    def __init__(self):
        """Initialize Gemini Calendar Processor with ACI integration and robust event creator"""
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize ACI calendar agents
        self.calendar_agents = AciCalendarAgents()
        
        # Initialize robust event creator
        self.event_creator = RobustEventCreator()
        
        # Bob's persona for beehive consultations
        self.bob_persona = """
        You are Bob, a friendly and knowledgeable beehive builder and consultant. You help people with:
        - Beehive construction and maintenance
        - Bee colony management
        - Honey extraction and processing
        - Beekeeping best practices
        - Equipment recommendations
        
        Your personality:
        - Warm, approachable, and patient
        - Expert in beekeeping but explains things simply
        - Always prioritizes safety and best practices
        - Enthusiastic about helping others start their beekeeping journey
        
        When scheduling appointments:
        - Be flexible and accommodating
        - Confirm all details clearly (date, time, location)
        - Provide helpful context about what to expect
        - Always confirm the appointment before ending the conversation
        """

    def process_message(self, message: str, phone_number: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """
        Process incoming message and determine if calendar operations are needed
        """
        if conversation_history is None:
            conversation_history = []
        
        # Check if message contains appointment-related keywords
        appointment_keywords = [
            'appointment', 'meet', 'schedule', 'booking', 'consultation',
            'visit', 'come by', 'see you', 'available', 'free time',
            'when can', 'what time', 'where to meet'
        ]
        
        message_lower = message.lower()
        is_appointment_related = any(keyword in message_lower for keyword in appointment_keywords)
        
        # Check for date/time/location patterns
        has_date_time_location = self._has_date_time_location(message)
        
        # Get current appointment context from robust event creator
        appointment_context = self._get_appointment_context(phone_number)
        
        if is_appointment_related or has_date_time_location or appointment_context:
            return self._handle_appointment_scheduling(message, phone_number, conversation_history)
        else:
            return self._handle_general_conversation(message, phone_number, conversation_history)

    def _has_date_time_location(self, message: str) -> bool:
        """Check if message contains date, time, or location information"""
        import re
        
        # Date patterns
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\btoday\b', r'\btomorrow\b', r'\bnext week\b'
        ]
        
        # Time patterns
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',  # HH:MM AM/PM
            r'\b\d{1,2}\s*(am|pm)\b',  # HH AM/PM
            r'\bmorning\b', r'\bafternoon\b', r'\bevening\b'
        ]
        
        # Location patterns
        location_patterns = [
            r'\bat\b', r'\bin\b', r'\blocation\b', r'\baddress\b', r'\bplace\b',
            r'\bhouse\b', r'\boffice\b', r'\bhome\b'
        ]
        
        has_date = any(re.search(pattern, message.lower()) for pattern in date_patterns)
        has_time = any(re.search(pattern, message.lower()) for pattern in time_patterns)
        has_location = any(re.search(pattern, message.lower()) for pattern in location_patterns)
        
        return has_date or has_time or has_location

    def _get_appointment_context(self, phone_number: str) -> Dict[str, Any]:
        """Get appointment context from robust event creator"""
        if phone_number in self.event_creator.appointments:
            return self.event_creator.appointments[phone_number]
        return {}

    def _handle_appointment_scheduling(self, message: str, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Handle appointment scheduling using robust event creator"""
        
        # Get current date context for grounding
        current_date_context = self.event_creator.get_current_date_context()
        
        # Extract appointment details using robust event creator
        extracted_details = self.event_creator.extract_appointment_details(message, phone_number)
        appointment_context = self._get_appointment_context(phone_number)
        
        print(f"[DEBUG] Current date context: {current_date_context}")
        print(f"[DEBUG] Extracted details: {extracted_details}")
        print(f"[DEBUG] Current context: {appointment_context}")
        
        # Check if user is confirming an appointment
        confirmation_keywords = ['yes', 'confirm', 'okay', 'sounds good', 'perfect', 'that works', 'sounds great']
        is_confirmation = any(keyword in message.lower() for keyword in confirmation_keywords)
        
        print(f"[DEBUG] Is confirmation: {is_confirmation}")
        print(f"[DEBUG] Pending confirmation: {appointment_context.get('status') == 'pending_confirmation'}")
        
        if is_confirmation and appointment_context.get('status') == 'pending_confirmation':
            return self._confirm_appointment(phone_number, conversation_history)
        
        # Check if we have a proposed date to check availability
        if extracted_details.date:
            availability_result = self.calendar_agents.check_availability_and_propose(
                extracted_details.date, 
                phone_number
            )
            
            if not availability_result['available']:
                # Date is busy, propose alternative
                extracted_details.date = availability_result['proposed_date']
                
                response = self._generate_response(
                    availability_result['message'],
                    phone_number,
                    conversation_history,
                    context_type="availability_check",
                    current_date_context=current_date_context
                )
                return response
        
        # Process appointment message using robust event creator
        result = self.event_creator.process_appointment_message(message, phone_number, conversation_history)
        
        # If appointment was created successfully, integrate with ACI calendar agents
        if result.get('appointment_created') and result.get('event_id'):
            # Create the event in Google Calendar via ACI
            event_details = {
                'title': f"Beehive Consultation - {result.get('client_name', 'Client')}",
                'date': extracted_details.date,
                'time': extracted_details.time,
                'location': extracted_details.location,
                'description': f"Beehive consultation appointment with {result.get('client_name', 'Client')} ({phone_number})"
            }
            
            calendar_result = self.calendar_agents.create_calendar_event(event_details, phone_number)
            
            if calendar_result['success']:
                result['calendar_event_id'] = calendar_result.get('event_id')
                result['response'] += f"\n\n✅ Appointment has been added to Google Calendar!"
            else:
                result['response'] += f"\n\n⚠️ Note: There was an issue adding to Google Calendar: {calendar_result.get('error')}"
        
        return result

    def _confirm_appointment(self, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Confirm and create appointment"""
        appointment_context = self._get_appointment_context(phone_number)
        
        if not appointment_context:
            return {
                "response": "I don't see any pending appointment to confirm. Let's start fresh - what would you like to schedule?",
                "appointment_created": False
            }
        
        # Use robust event creator to handle confirmation
        result = self.event_creator.process_appointment_message("yes", phone_number, conversation_history)
        
        # If appointment was created, integrate with ACI calendar
        if result.get('appointment_created'):
            details = appointment_context.get('details', {})
            event_details = {
                'title': f"Beehive Consultation - {details.get('client_name', 'Client')}",
                'date': details.get('date'),
                'time': details.get('time'),
                'location': details.get('location'),
                'description': f"Beehive consultation appointment with {details.get('client_name', 'Client')} ({phone_number})"
            }
            
            calendar_result = self.calendar_agents.create_calendar_event(event_details, phone_number)
            
            if calendar_result['success']:
                result['calendar_event_id'] = calendar_result.get('event_id')
                result['response'] += f"\n\n✅ Appointment has been added to Google Calendar!"
            else:
                result['response'] += f"\n\n⚠️ Note: There was an issue adding to Google Calendar: {calendar_result.get('error')}"
        
        return result

    def _handle_general_conversation(self, message: str, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Handle general beehive-related conversation"""
        return self._generate_response(
            message,
            phone_number,
            conversation_history,
            context_type="general"
        )

    def _generate_response(self, message: str, phone_number: str, conversation_history: List[Dict], 
                          context_type: str = "general", appointment_context: Dict[str, Any] = None, 
                          current_date_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate response using Gemini with proper context
        """
        try:
            # Get current date context if not provided
            if current_date_context is None:
                current_date_context = self.event_creator.get_current_date_context()
            
            # Get appointment context if not provided
            if appointment_context is None:
                appointment_context = self._get_appointment_context(phone_number)
            
            # Generate prompt with robust event creator
            prompt = self.event_creator.generate_appointment_prompt(
                message, 
                phone_number, 
                appointment_context
            )
            
            # Add conversation history context
            if conversation_history:
                history_text = "\n\nCONVERSATION HISTORY:\n"
                for entry in conversation_history[-5:]:  # Last 5 messages
                    history_text += f"- {entry.get('role', 'user')}: {entry.get('content', '')}\n"
                prompt += history_text
            
            # Generate response using Gemini
            response = self.model.generate_content(prompt)
            
            # Check if response contains appointment-related content
            response_text = response.text.strip()
            
            # Extract any appointment details from the response
            extracted_details = self.event_creator.extract_appointment_details(response_text, phone_number)
            
            return {
                "response": response_text,
                "is_greeting": self._is_greeting(message),
                "timestamp": datetime.now().isoformat(),
                "phone_number": phone_number,
                "appointment_related": context_type != "general",
                "extracted_details": {
                    "date": extracted_details.date,
                    "time": extracted_details.time,
                    "location": extracted_details.location,
                    "client_name": extracted_details.client_name
                } if any([extracted_details.date, extracted_details.time, extracted_details.location, extracted_details.client_name]) else None
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to generate response: {e}")
            return {
                "response": "I'm having trouble processing that right now. Could you try rephrasing your message?",
                "is_greeting": False,
                "timestamp": datetime.now().isoformat(),
                "phone_number": phone_number,
                "error": str(e)
            }

    def _is_greeting(self, message: str) -> bool:
        """Check if message is a greeting"""
        greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
        return any(greeting in message.lower() for greeting in greetings)

# Example usage
if __name__ == "__main__":
    processor = GeminiCalendarProcessor()
    
    # Test appointment scheduling
    test_message = "Hi Bob, I'd like to schedule a consultation for tomorrow at 2 PM at my house"
    result = processor.process_message(test_message, "+1234567890")
    print(f"Test Result: {result}") 