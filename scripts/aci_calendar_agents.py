import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from aci import ACI
from robust_event_creator import RobustEventCreator, AppointmentDetails

class AciCalendarAgents:
    def __init__(self):
        """Initialize ACI calendar agents with separate API keys and robust event creator"""
        # Initialize separate ACI clients for different agents
        self.calendar_reader_aci = ACI(api_key=os.getenv('ACI_CALENDAR_READER_API_KEY'))
        self.event_creator_aci = ACI(api_key=os.getenv('ACI_EVENT_CREATOR_API_KEY'))
        
        # Use fallback to single API key if separate keys not provided
        if not os.getenv('ACI_CALENDAR_READER_API_KEY') and os.getenv('ACI_API_KEY'):
            self.calendar_reader_aci = ACI(api_key=os.getenv('ACI_API_KEY'))
        if not os.getenv('ACI_EVENT_CREATOR_API_KEY') and os.getenv('ACI_API_KEY'):
            self.event_creator_aci = ACI(api_key=os.getenv('ACI_API_KEY'))
        
        self.linked_account_owner_id = os.getenv('LINKED_ACCOUNT_OWNER_ID')
        
        # Initialize robust event creator
        self.event_creator = RobustEventCreator()
        
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
        Calendar Event Creator Agent: Create a new calendar event with robust validation
        """
        try:
            print(f"[DEBUG] Calendar Creator: Creating event with details {event_details}")
            
            # Validate required fields using robust event creator
            required_fields = ['title', 'date', 'time', 'location']
            missing_fields = [field for field in required_fields if not event_details.get(field)]
            
            if missing_fields:
                return {
                    "success": False,
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                }
            
            # Create AppointmentDetails object for validation
            appointment_details = AppointmentDetails(
                date=event_details.get('date'),
                time=event_details.get('time'),
                location=event_details.get('location'),
                client_name=event_details.get('title', '').replace('Beehive Consultation - ', ''),
                duration=event_details.get('duration', 60)
            )
            
            # Validate appointment details
            is_valid, errors = self.event_creator.validate_appointment_details(appointment_details)
            if not is_valid:
                return {
                    "success": False,
                    "error": f"Validation failed: {', '.join(errors)}"
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
            
            # Calculate start and end times
            start_time = datetime.strptime(f"{appointment_details.date}T{appointment_details.time}", "%Y-%m-%dT%H:%M")
            end_time = start_time + timedelta(minutes=appointment_details.duration)
            
            # Prepare event data for Google Calendar with proper formatting
            event_data = {
                "summary": f"Beehive Consultation - {appointment_details.client_name}",
                "description": event_details.get('description', f'Beehive consultation appointment with {appointment_details.client_name} ({phone_number})'),
                "start": {
                    "dateTime": start_time.isoformat(),
                    "timeZone": "America/New_York"  # Configurable timezone
                },
                "end": {
                    "dateTime": end_time.isoformat(),
                    "timeZone": "America/New_York"
                },
                "location": appointment_details.location,
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
            
            print(f"[DEBUG] Calendar Creator: Event data prepared: {event_data}")
            
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
                "event_details": {
                    "date": appointment_details.date,
                    "time": appointment_details.time,
                    "location": appointment_details.location,
                    "client_name": appointment_details.client_name,
                    "duration": appointment_details.duration
                },
                "google_calendar_data": event_data
            }
            
        except Exception as e:
            print(f"[ERROR] Calendar Creator failed: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def check_availability_and_propose(self, proposed_date: str, phone_number: str) -> Dict[str, Any]:
        """
        Check calendar availability for a proposed date and suggest alternatives if busy
        """
        try:
            print(f"[DEBUG] Checking availability for {proposed_date}")
            
            # Get events for the proposed date
            events_result = self.get_calendar_events(proposed_date, phone_number)
            
            if not events_result['success']:
                return {
                    "available": True,  # Assume available if we can't check
                    "proposed_date": proposed_date,
                    "message": "I can't check my calendar right now, but let's assume that date works. What time would you prefer?"
                }
            
            events = events_result['events']
            
            # Check if the date is busy (more than 3 events or specific time conflicts)
            if len(events) >= 3:
                # Date is busy, find next available date
                next_available = self._find_next_available_date(proposed_date, phone_number)
                
                return {
                    "available": False,
                    "proposed_date": next_available,
                    "message": f"I'm quite busy on {proposed_date}. How about {next_available} instead? What time works best for you?"
                }
            
            # Check for specific time conflicts (simplified check)
            # In a real implementation, you'd check for specific time slots
            return {
                "available": True,
                "proposed_date": proposed_date,
                "message": f"Great! {proposed_date} looks good. What time would you prefer for our consultation?"
            }
            
        except Exception as e:
            print(f"[ERROR] Availability check failed: {e}")
            return {
                "available": True,
                "proposed_date": proposed_date,
                "message": "I can't check my calendar right now, but let's assume that date works. What time would you prefer?"
            }

    def _find_next_available_date(self, start_date: str, phone_number: str, max_days: int = 7) -> str:
        """
        Find the next available date within max_days
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            
            for i in range(1, max_days + 1):
                check_date = start + timedelta(days=i)
                check_date_str = check_date.strftime("%Y-%m-%d")
                
                events_result = self.get_calendar_events(check_date_str, phone_number)
                
                if events_result['success'] and len(events_result['events']) < 3:
                    return check_date_str
            
            # If no available date found, return the original date
            return start_date
            
        except Exception as e:
            print(f"[ERROR] Finding next available date failed: {e}")
            return start_date

    def extract_appointment_details(self, message: str) -> Dict[str, Any]:
        """
        Extract appointment details using robust event creator
        """
        # Use robust event creator for extraction
        details = self.event_creator.extract_appointment_details(message, "unknown")
        
        return {
            "date": details.date,
            "time": details.time,
            "location": details.location,
            "client_name": details.client_name,
            "duration": details.duration
        }

    def get_current_date_context(self) -> Dict[str, Any]:
        """
        Get current date context using robust event creator
        """
        return self.event_creator.get_current_date_context()

    def update_appointment_context(self, phone_number: str, context: Dict[str, Any]):
        """
        Update appointment context using robust event creator
        """
        if phone_number not in self.event_creator.appointments:
            self.event_creator.appointments[phone_number] = {
                "status": "gathering_info",
                "details": {},
                "created_at": datetime.now().isoformat()
            }
        
        # Update details
        if 'details' in context:
            self.event_creator.appointments[phone_number]['details'].update(context['details'])
        
        # Update status
        if 'status' in context:
            self.event_creator.appointments[phone_number]['status'] = context['status']

    def get_appointment_context(self, phone_number: str) -> Dict[str, Any]:
        """
        Get appointment context using robust event creator
        """
        return self.event_creator.appointments.get(phone_number, {})

    def clear_appointment_context(self, phone_number: str):
        """
        Clear appointment context using robust event creator
        """
        if phone_number in self.event_creator.appointments:
            del self.event_creator.appointments[phone_number]

    def get_api_key_status(self) -> Dict[str, Any]:
        """
        Check API key status for both calendar agents
        """
        return {
            "calendar_reader_api_key": bool(os.getenv('ACI_CALENDAR_READER_API_KEY')),
            "event_creator_api_key": bool(os.getenv('ACI_EVENT_CREATOR_API_KEY')),
            "fallback_api_key": bool(os.getenv('ACI_API_KEY')),
            "linked_account_owner_id": bool(os.getenv('LINKED_ACCOUNT_OWNER_ID'))
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