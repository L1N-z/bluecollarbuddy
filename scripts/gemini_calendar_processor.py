import os
import json
import google.generativeai as genai
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from aci_calendar_agents import AciCalendarAgents

class GeminiCalendarProcessor:
    def __init__(self):
        """Initialize Gemini Calendar Processor with ACI integration"""
        # Configure Gemini
        genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Initialize ACI calendar agents
        self.calendar_agents = AciCalendarAgents()
        
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
        
        # Get current appointment context
        appointment_context = self.calendar_agents.get_appointment_context(phone_number)
        
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

    def _handle_appointment_scheduling(self, message: str, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Handle appointment scheduling logic"""
        
        # Extract appointment details from message
        extracted_details = self.calendar_agents.extract_appointment_details(message)
        appointment_context = self.calendar_agents.get_appointment_context(phone_number)
        
        # Update context with extracted details
        if extracted_details['date']:
            appointment_context['proposed_date'] = extracted_details['date']
        if extracted_details['time']:
            appointment_context['proposed_time'] = extracted_details['time']
        if extracted_details['location']:
            appointment_context['proposed_location'] = extracted_details['location']
        
        # Check if user is confirming an appointment
        confirmation_keywords = ['yes', 'confirm', 'okay', 'sounds good', 'perfect', 'that works']
        is_confirmation = any(keyword in message.lower() for keyword in confirmation_keywords)
        
        if is_confirmation and appointment_context.get('pending_confirmation'):
            return self._confirm_appointment(phone_number, conversation_history)
        
        # Check if we have a proposed date to check availability
        if appointment_context.get('proposed_date'):
            availability_result = self.calendar_agents.check_availability_and_propose(
                appointment_context['proposed_date'], 
                phone_number
            )
            
            if not availability_result['available']:
                # Date is busy, propose alternative
                appointment_context['proposed_date'] = availability_result['proposed_date']
                self.calendar_agents.update_appointment_context(phone_number, appointment_context)
                
                response = self._generate_response(
                    availability_result['message'],
                    phone_number,
                    conversation_history,
                    context_type="availability_check"
                )
                return response
        
        # Check if we have all required details for appointment creation
        if self._has_complete_appointment_details(appointment_context):
            return self._create_appointment(phone_number, conversation_history)
        
        # Generate response to gather missing details
        response = self._generate_response(
            message,
            phone_number,
            conversation_history,
            context_type="appointment_gathering",
            appointment_context=appointment_context
        )
        
        # Update context
        self.calendar_agents.update_appointment_context(phone_number, appointment_context)
        
        return response

    def _has_complete_appointment_details(self, context: Dict[str, Any]) -> bool:
        """Check if we have all required appointment details"""
        required_fields = ['proposed_date', 'proposed_time', 'proposed_location']
        return all(context.get(field) for field in required_fields)

    def _create_appointment(self, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Create the calendar appointment"""
        appointment_context = self.calendar_agents.get_appointment_context(phone_number)
        
        # Create event details
        event_details = {
            'title': 'Beehive Consultation with Bob',
            'date': appointment_context['proposed_date'],
            'time': appointment_context['proposed_time'],
            'location': appointment_context['proposed_location'],
            'description': f'Beehive consultation appointment with {phone_number}'
        }
        
        # Create calendar event
        creation_result = self.calendar_agents.create_calendar_event(event_details, phone_number)
        
        if creation_result['success']:
            # Mark as pending confirmation
            appointment_context['pending_confirmation'] = True
            appointment_context['event_id'] = creation_result['event_id']
            self.calendar_agents.update_appointment_context(phone_number, appointment_context)
            
            # Generate confirmation message
            confirmation_message = self._format_appointment_confirmation(event_details)
            
            response = self._generate_response(
                confirmation_message,
                phone_number,
                conversation_history,
                context_type="appointment_created"
            )
            
            return response
        else:
            # Handle creation failure
            error_message = f"I'm having trouble creating the appointment. {creation_result.get('error', 'Please try again.')}"
            
            response = self._generate_response(
                error_message,
                phone_number,
                conversation_history,
                context_type="appointment_error"
            )
            
            return response

    def _confirm_appointment(self, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Handle appointment confirmation"""
        appointment_context = self.calendar_agents.get_appointment_context(phone_number)
        
        # Clear the appointment context
        self.calendar_agents.clear_appointment_context(phone_number)
        
        # Generate final confirmation message
        response = self._generate_response(
            "Great, see you then! 🐝",
            phone_number,
            conversation_history,
            context_type="appointment_confirmed"
        )
        
        return response

    def _format_appointment_confirmation(self, event_details: Dict[str, Any]) -> str:
        """Format appointment confirmation message"""
        return f"""Perfect! I've scheduled our beehive consultation:

📅 Date: {event_details['date']}
⏰ Time: {event_details['time']}
📍 Location: {event_details['location']}

Please confirm if these details work for you, and I'll see you there! 🐝"""

    def _handle_general_conversation(self, message: str, phone_number: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Handle general beehive-related conversation"""
        return self._generate_response(
            message,
            phone_number,
            conversation_history,
            context_type="general"
        )

    def _generate_response(self, message: str, phone_number: str, conversation_history: List[Dict], 
                          context_type: str = "general", appointment_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate response using Gemini with context"""
        
        # Build system prompt based on context type
        system_prompt = self.bob_persona
        
        if context_type == "appointment_gathering":
            system_prompt += f"""

You are currently helping schedule an appointment. Current context:
- Date: {appointment_context.get('proposed_date', 'Not specified')}
- Time: {appointment_context.get('proposed_time', 'Not specified')}
- Location: {appointment_context.get('proposed_location', 'Not specified')}

Help gather the missing information in a friendly way. Ask for specific details like:
- "What time works best for you?"
- "Where would you like to meet?"
- "What date would you prefer?"

Be helpful and specific in your questions."""
        
        elif context_type == "availability_check":
            system_prompt += """

The user proposed a date that was busy. You've suggested an alternative date.
Be helpful and ask for their preferred time for the new date."""
        
        elif context_type == "appointment_created":
            system_prompt += """

You've just created an appointment and are asking for confirmation.
Be enthusiastic and clear about the details. Wait for their confirmation."""
        
        elif context_type == "appointment_confirmed":
            system_prompt += """

The user has confirmed the appointment. Send a brief, friendly confirmation message."""
        
        # Build conversation for Gemini
        conversation = []
        
        # Add system message
        conversation.append({
            "role": "user",
            "parts": [f"System: {system_prompt}\n\nUser message: {message}"]
        })
        
        # Add conversation history (last 5 messages to stay within context limits)
        for msg in conversation_history[-5:]:
            if msg.get('role') == 'user':
                conversation.append({
                    "role": "user",
                    "parts": [msg.get('content', '')]
                })
            elif msg.get('role') == 'assistant':
                conversation.append({
                    "role": "model",
                    "parts": [msg.get('content', '')]
                })
        
        try:
            # Generate response
            response = self.model.generate_content(conversation)
            
            return {
                "success": True,
                "response": response.text,
                "context_type": context_type,
                "appointment_context": appointment_context
            }
            
        except Exception as e:
            print(f"[ERROR] Gemini response generation failed: {e}")
            return {
                "success": False,
                "response": "I'm having trouble processing your message right now. Could you try again?",
                "error": str(e),
                "context_type": context_type
            }

# Example usage
if __name__ == "__main__":
    processor = GeminiCalendarProcessor()
    
    # Test appointment scheduling
    test_message = "Hi Bob, I'd like to schedule a consultation for tomorrow at 2 PM at my house"
    result = processor.process_message(test_message, "+1234567890")
    print(f"Test Result: {result}") 