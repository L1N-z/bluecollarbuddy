import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from aci import ACI

class AciCalendarAgents:
    def __init__(self):
        """Initialize ACI calendar agents"""
        self.aci = ACI(api_key=os.getenv('ACI_API_KEY'))
        self.linked_account_owner_id = os.getenv('LINKED_ACCOUNT_OWNER_ID')
        
        # Initialize calendar tools
        self.calendar_tools = [
            {
                "name": "ACI_SEARCH_FUNCTIONS",
                "description": "Search for available calendar functions"
            },
            {
                "name": "ACI_EXECUTE_FUNCTION", 
                "description": "Execute a specific calendar function"
            }
        ]
        
        # Store conversation context for appointment scheduling
        self.appointment_contexts = {}

    def get_calendar_events(self, date: str, phone_number: str) -> Dict[str, Any]:
        """
        Calendar Reader Agent: Check events on a specific date
        Returns events with details or empty list if no events
        """
        try:
            print(f"[DEBUG] Calendar Reader: Checking events for {date}")
            
            # Search for calendar functions
            search_result = self.aci.search_functions(
                query="calendar events list read",
                linked_account_owner_id=self.linked_account_owner_id
            )
            
            if not search_result.get('functions'):
                return {
                    "success": False,
                    "error": "No calendar functions found",
                    "events": []
                }
            
            # Execute calendar read function
            calendar_function = search_result['functions'][0]
            
            execute_result = self.aci.execute_function(
                function_name=calendar_function['name'],
                arguments={
                    "date": date,
                    "linked_account_owner_id": self.linked_account_owner_id
                }
            )
            
            events = execute_result.get('result', [])
            
            print(f"[DEBUG] Calendar Reader: Found {len(events)} events for {date}")
            
            return {
                "success": True,
                "date": date,
                "events": events,
                "count": len(events)
            }
            
        except Exception as e:
            print(f"[ERROR] Calendar Reader failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "events": []
            }

    def create_calendar_event(self, event_details: Dict[str, Any], phone_number: str) -> Dict[str, Any]:
        """
        Calendar Event Creator Agent: Create a new calendar event
        """
        try:
            print(f"[DEBUG] Calendar Creator: Creating event with details {event_details}")
            
            # Search for calendar creation functions
            search_result = self.aci.search_functions(
                query="calendar event create add",
                linked_account_owner_id=self.linked_account_owner_id
            )
            
            if not search_result.get('functions'):
                return {
                    "success": False,
                    "error": "No calendar creation functions found"
                }
            
            # Execute calendar creation function
            create_function = search_result['functions'][0]
            
            execute_result = self.aci.execute_function(
                function_name=create_function['name'],
                arguments={
                    "title": event_details.get('title', 'Beehive Consultation'),
                    "date": event_details.get('date'),
                    "time": event_details.get('time'),
                    "location": event_details.get('location'),
                    "description": event_details.get('description', 'Beehive consultation with Bob'),
                    "linked_account_owner_id": self.linked_account_owner_id
                }
            )
            
            print(f"[DEBUG] Calendar Creator: Event created successfully")
            
            return {
                "success": True,
                "event_id": execute_result.get('result', {}).get('id'),
                "event_details": event_details
            }
            
        except Exception as e:
            print(f"[ERROR] Calendar Creator failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def check_availability_and_propose(self, proposed_date: str, phone_number: str) -> Dict[str, Any]:
        """
        Check if a proposed date is available and propose alternatives if needed
        """
        try:
            # Check events on proposed date
            events_result = self.get_calendar_events(proposed_date, phone_number)
            
            if not events_result['success']:
                return {
                    "available": False,
                    "message": "I'm having trouble checking my calendar right now. Could you try a different date?",
                    "proposed_date": proposed_date
                }
            
            if events_result['count'] == 0:
                # Date is free
                return {
                    "available": True,
                    "message": f"Perfect! I'm free on {proposed_date}. What time works best for you?",
                    "proposed_date": proposed_date,
                    "events": []
                }
            else:
                # Date is busy, propose next available day
                next_date = self._find_next_available_date(proposed_date, phone_number)
                
                return {
                    "available": False,
                    "message": f"Unfortunately I'm not free on {proposed_date}. How about {next_date} instead?",
                    "proposed_date": next_date,
                    "conflicting_events": events_result['events']
                }
                
        except Exception as e:
            print(f"[ERROR] Availability check failed: {e}")
            return {
                "available": False,
                "message": "I'm having trouble checking my calendar. Could you try again?",
                "proposed_date": proposed_date
            }

    def _find_next_available_date(self, start_date: str, phone_number: str, max_days: int = 7) -> str:
        """
        Find the next available date within max_days
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            
            for i in range(1, max_days + 1):
                next_date = start + timedelta(days=i)
                next_date_str = next_date.strftime("%Y-%m-%d")
                
                events_result = self.get_calendar_events(next_date_str, phone_number)
                
                if events_result['success'] and events_result['count'] == 0:
                    return next_date_str
            
            # If no free days found, return the original date + 1 day
            return (start + timedelta(days=1)).strftime("%Y-%m-%d")
            
        except Exception as e:
            print(f"[ERROR] Finding next available date failed: {e}")
            # Return tomorrow as fallback
            tomorrow = datetime.now() + timedelta(days=1)
            return tomorrow.strftime("%Y-%m-%d")

    def extract_appointment_details(self, message: str) -> Dict[str, Any]:
        """
        Extract appointment details from user message
        """
        details = {
            "date": None,
            "time": None,
            "location": None,
            "has_all_details": False
        }
        
        # Simple date/time/location extraction (you can enhance this with NLP)
        message_lower = message.lower()
        
        # Extract date patterns (YYYY-MM-DD, MM/DD/YYYY, etc.)
        import re
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                details["date"] = match.group()
                break
        
        # Extract time patterns
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',  # HH:MM AM/PM
            r'\b\d{1,2}\s*(am|pm)\b',  # HH AM/PM
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                details["time"] = match.group()
                break
        
        # Extract location (simple keyword-based)
        location_keywords = ['at', 'in', 'location', 'address', 'place']
        words = message_lower.split()
        
        for i, word in enumerate(words):
            if word in location_keywords and i + 1 < len(words):
                # Extract next few words as location
                location_parts = words[i+1:i+4]  # Take up to 3 words
                details["location"] = ' '.join(location_parts)
                break
        
        # Check if we have all required details
        details["has_all_details"] = all([
            details["date"], 
            details["time"], 
            details["location"]
        ])
        
        return details

    def update_appointment_context(self, phone_number: str, context: Dict[str, Any]):
        """
        Update appointment context for a phone number
        """
        if phone_number not in self.appointment_contexts:
            self.appointment_contexts[phone_number] = {}
        
        self.appointment_contexts[phone_number].update(context)

    def get_appointment_context(self, phone_number: str) -> Dict[str, Any]:
        """
        Get appointment context for a phone number
        """
        return self.appointment_contexts.get(phone_number, {})

    def clear_appointment_context(self, phone_number: str):
        """
        Clear appointment context for a phone number
        """
        if phone_number in self.appointment_contexts:
            del self.appointment_contexts[phone_number]

# Example usage and testing
if __name__ == "__main__":
    # Test the calendar agents
    agents = AciCalendarAgents()
    
    # Test calendar reader
    events = agents.get_calendar_events("2025-06-22", "test_phone")
    print(f"Calendar Reader Test: {events}")
    
    # Test availability check
    availability = agents.check_availability_and_propose("2025-06-22", "test_phone")
    print(f"Availability Test: {availability}")
    
    # Test appointment details extraction
    details = agents.extract_appointment_details("Can we meet on 2025-06-22 at 2:00 PM at my house?")
    print(f"Details Extraction Test: {details}") 