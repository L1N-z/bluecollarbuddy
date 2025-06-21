import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from aci import ACI

class AciCalendarAgents:
    def __init__(self):
        """Initialize ACI calendar agents with separate API keys"""
        # Initialize separate ACI clients for different agents
        self.calendar_reader_aci = ACI(api_key=os.getenv('ACI_CALENDAR_READER_API_KEY'))
        self.event_creator_aci = ACI(api_key=os.getenv('ACI_EVENT_CREATOR_API_KEY'))
        
        # Use fallback to single API key if separate keys not provided
        if not os.getenv('ACI_CALENDAR_READER_API_KEY') and os.getenv('ACI_API_KEY'):
            self.calendar_reader_aci = ACI(api_key=os.getenv('ACI_API_KEY'))
        if not os.getenv('ACI_EVENT_CREATOR_API_KEY') and os.getenv('ACI_API_KEY'):
            self.event_creator_aci = ACI(api_key=os.getenv('ACI_API_KEY'))
        
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
            
            # Search for calendar functions using Calendar Reader API key
            search_result = self.calendar_reader_aci.search_functions(
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
            
            execute_result = self.calendar_reader_aci.execute_function(
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
            
            # Validate required fields
            required_fields = ['title', 'date', 'time', 'location']
            missing_fields = [field for field in required_fields if not event_details.get(field)]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Search for calendar creation functions using Event Creator API key
            search_result = self.event_creator_aci.search_functions(
                query="google calendar event create add",
                linked_account_owner_id=self.linked_account_owner_id
            )
            
            if not search_result.get('functions'):
                return {
                    "success": False,
                    "error": "No Google Calendar creation functions found"
                }
            
            # Execute calendar creation function
            create_function = search_result['functions'][0]
            
            # Prepare event data for Google Calendar
            event_data = {
                "summary": event_details.get('title', 'Beehive Consultation with Bob'),
                "description": event_details.get('description', f'Beehive consultation appointment with {phone_number}'),
                "start": {
                    "dateTime": f"{event_details['date']}T{self._convert_time_to_24hr(event_details['time'])}:00",
                    "timeZone": "America/New_York"  # Default timezone, can be made configurable
                },
                "end": {
                    "dateTime": f"{event_details['date']}T{self._convert_time_to_24hr(event_details['time'], add_hours=1)}:00",
                    "timeZone": "America/New_York"
                },
                "location": event_details.get('location', ''),
                "attendees": [
                    {"email": f"{phone_number}@example.com"}  # Placeholder email
                ],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},  # 1 day before
                        {"method": "popup", "minutes": 30}  # 30 minutes before
                    ]
                }
            }
            
            execute_result = self.event_creator_aci.execute_function(
                function_name=create_function['name'],
                arguments={
                    "event_data": event_data,
                    "linked_account_owner_id": self.linked_account_owner_id
                }
            )
            
            print(f"[DEBUG] Calendar Creator: Event created successfully")
            
            return {
                "success": True,
                "event_id": execute_result.get('result', {}).get('id'),
                "event_details": event_details,
                "google_calendar_data": event_data
            }
            
        except Exception as e:
            print(f"[ERROR] Calendar Creator failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _convert_time_to_24hr(self, time_str: str, add_hours: int = 0) -> str:
        """
        Convert time string to 24-hour format for Google Calendar
        """
        import re
        from datetime import datetime, timedelta
        
        # Handle various time formats
        time_lower = time_str.lower().strip()
        
        # Extract hours and minutes
        time_pattern = r'(\d{1,2}):?(\d{2})?\s*(am|pm)?'
        match = re.match(time_pattern, time_lower)
        
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2)) if match.group(2) else 0
            period = match.group(3)
            
            # Convert to 24-hour format
            if period == 'pm' and hours != 12:
                hours += 12
            elif period == 'am' and hours == 12:
                hours = 0
            
            # Add hours if specified (for end time)
            if add_hours > 0:
                time_obj = datetime.now().replace(hour=hours, minute=minutes)
                time_obj += timedelta(hours=add_hours)
                hours = time_obj.hour
                minutes = time_obj.minute
            
            return f"{hours:02d}:{minutes:02d}"
        
        # Handle natural language times
        time_map = {
            'morning': '09:00',
            'afternoon': '14:00',
            'evening': '18:00',
            'night': '20:00'
        }
        
        if time_lower in time_map:
            base_time = time_map[time_lower]
            if add_hours > 0:
                time_obj = datetime.strptime(base_time, "%H:%M")
                time_obj += timedelta(hours=add_hours)
                return time_obj.strftime("%H:%M")
            return base_time
        
        # Fallback
        return "14:00"

    def check_availability_and_propose(self, proposed_date: str, phone_number: str) -> Dict[str, Any]:
        """
        Check if a proposed date is available and propose alternatives if needed
        """
        try:
            # Check events on proposed date using Calendar Reader
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
        from datetime import datetime, timedelta
        
        # Enhanced date patterns including natural language
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
        ]
        
        # Check for natural language date expressions
        natural_date_patterns = [
            r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\bthis\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\btomorrow\b',
            r'\btoday\b'
        ]
        
        # Try exact date patterns first
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                details["date"] = match.group()
                break
        
        # If no exact date found, try natural language
        if not details["date"]:
            for pattern in natural_date_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    natural_date = match.group()
                    details["date"] = self._convert_natural_date(natural_date)
                    break
        
        # Enhanced time patterns including natural language
        time_patterns = [
            r'\b\d{1,2}:\d{2}\s*(am|pm)?\b',  # HH:MM AM/PM
            r'\b\d{1,2}\s*(am|pm)\b',  # HH AM/PM
        ]
        
        # Check for natural language time expressions
        natural_time_patterns = [
            r'\bmorning\b',
            r'\bafternoon\b', 
            r'\bevening\b',
            r'\bnight\b'
        ]
        
        # Try exact time patterns first
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                details["time"] = match.group()
                break
        
        # If no exact time found, try natural language
        if not details["time"]:
            for pattern in natural_time_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    natural_time = match.group()
                    details["time"] = self._convert_natural_time(natural_time)
                    break
        
        # Enhanced location extraction
        location_keywords = ['at', 'in', 'location', 'address', 'place', 'here', 'there']
        words = message_lower.split()
        
        # Look for location patterns
        for i, word in enumerate(words):
            if word in location_keywords and i + 1 < len(words):
                # Extract next few words as location
                location_parts = words[i+1:i+4]  # Take up to 3 words
                details["location"] = ' '.join(location_parts)
                break
        
        # If no location found, check for common location patterns
        if not details["location"]:
            location_patterns = [
                r'\bmy\s+(house|home|place)\b',
                r'\byour\s+(house|home|place|office)\b',
                r'\bhere\b',
                r'\bthere\b'
            ]
            
            for pattern in location_patterns:
                match = re.search(pattern, message_lower)
                if match:
                    details["location"] = match.group()
                    break
        
        # Check if we have all required details
        details["has_all_details"] = all([
            details["date"], 
            details["time"], 
            details["location"]
        ])
        
        return details

    def _convert_natural_date(self, natural_date: str) -> str:
        """
        Convert natural language date to YYYY-MM-DD format using current date as grounding
        """
        today = datetime.now()
        
        if natural_date == "tomorrow":
            return (today + timedelta(days=1)).strftime("%Y-%m-%d")
        elif natural_date == "today":
            return today.strftime("%Y-%m-%d")
        elif "next" in natural_date:
            # Handle "next Tuesday" etc.
            day_name = natural_date.split()[-1].lower()
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            if day_name in day_map:
                target_day = day_map[day_name]
                current_day = today.weekday()
                days_ahead = target_day - current_day
                
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        elif "this" in natural_date:
            # Handle "this Tuesday" etc.
            day_name = natural_date.split()[-1].lower()
            day_map = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
                'friday': 4, 'saturday': 5, 'sunday': 6
            }
            
            if day_name in day_map:
                target_day = day_map[day_name]
                current_day = today.weekday()
                days_ahead = target_day - current_day
                
                if days_ahead < 0:  # Target day already happened this week
                    return None  # Invalid - can't schedule in the past
                
                return (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        return None

    def _convert_natural_time(self, natural_time: str) -> str:
        """
        Convert natural language time to standard format
        """
        time_map = {
            'morning': '9:00 AM',
            'afternoon': '2:00 PM', 
            'evening': '6:00 PM',
            'night': '8:00 PM'
        }
        
        return time_map.get(natural_time, natural_time)

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

    def get_api_key_status(self) -> Dict[str, Any]:
        """
        Get status of API keys for debugging
        """
        return {
            "calendar_reader_api_key": "set" if os.getenv('ACI_CALENDAR_READER_API_KEY') else "not_set",
            "event_creator_api_key": "set" if os.getenv('ACI_EVENT_CREATOR_API_KEY') else "not_set",
            "fallback_api_key": "set" if os.getenv('ACI_API_KEY') else "not_set",
            "linked_account_owner_id": "set" if self.linked_account_owner_id else "not_set"
        }

    def get_current_date_context(self) -> str:
        """
        Get current date context for grounding
        """
        today = datetime.now()
        return {
            "current_date": today.strftime("%Y-%m-%d"),
            "current_day": today.strftime("%A"),
            "current_time": today.strftime("%I:%M %p")
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the calendar agents
    agents = AciCalendarAgents()
    
    # Test API key status
    print(f"API Key Status: {agents.get_api_key_status()}")
    
    # Test calendar reader
    events = agents.get_calendar_events("2025-06-22", "test_phone")
    print(f"Calendar Reader Test: {events}")
    
    # Test availability check
    availability = agents.check_availability_and_propose("2025-06-22", "test_phone")
    print(f"Availability Test: {availability}")
    
    # Test appointment details extraction
    details = agents.extract_appointment_details("Can we meet on 2025-06-22 at 2:00 PM at my house?")
    print(f"Details Extraction Test: {details}") 