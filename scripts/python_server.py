import os
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging
from datetime import datetime
import asyncio

# Import our processors
from gemini_message_processor import GeminiMessageProcessor
from gemini_calendar_processor import GeminiCalendarProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Blue Collar Buddy API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize processors
gemini_processor = GeminiMessageProcessor()
calendar_processor = GeminiCalendarProcessor()

# Store Bob's settings
bob_account = None
agent_settings = {
    "enabled": True,
    "delayTime": 5,
    "defaultGreeting": ""
}

# Store conversation history
conversation_history = {}

class MessageRequest(BaseModel):
    message: str
    phone_number: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class CalendarRequest(BaseModel):
    date: str
    phone_number: str

class AppointmentRequest(BaseModel):
    message: str
    phone_number: str
    conversation_history: Optional[List[Dict[str, Any]]] = None

class EventCreationRequest(BaseModel):
    event_details: Dict[str, Any]
    phone_number: str

class SettingsUpdate(BaseModel):
    bobAccount: Optional[Dict[str, Any]] = None
    agentSettings: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Blue Collar Buddy API"}

@app.post("/process-message")
async def process_message(request: MessageRequest):
    """
    Process general messages using the original Gemini processor
    """
    try:
        # Check if agent is enabled
        if not agent_settings.get("enabled", True):
            return {
                "response": "Agent is currently disabled. Please enable it in the dashboard.",
                "agent_disabled": True
            }
        
        # Apply delay if configured
        delay_time = agent_settings.get("delayTime", 5)
        if delay_time > 0:
            await asyncio.sleep(delay_time)
        
        # Get conversation history
        history = conversation_history.get(request.phone_number, [])
        if request.conversation_history:
            history = request.conversation_history
        
        # Process the message
        result = gemini_processor.process_message(
            request.message,
            request.phone_number,
            history
        )
        
        # Update conversation history
        if request.phone_number not in conversation_history:
            conversation_history[request.phone_number] = []
        
        conversation_history[request.phone_number].append({
            "role": "user",
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        })
        
        conversation_history[request.phone_number].append({
            "role": "assistant",
            "content": result.get("response", ""),
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 20 messages
        conversation_history[request.phone_number] = conversation_history[request.phone_number][-20:]
        
        # Check if response should be paused (for pricing discussions)
        if result.get("response") == "PAUSE":
            return {
                "response": "PAUSE",
                "message": "Pricing discussion requires Bob's direct intervention. Please wait for Bob to respond.",
                "pause_required": True
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-appointment")
async def process_appointment(request: AppointmentRequest):
    """
    Process appointment-related messages using the calendar processor
    """
    try:
        logger.info(f"Processing appointment message for {request.phone_number}: {request.message[:50]}...")
        
        result = calendar_processor.process_message(
            request.message,
            request.phone_number,
            request.conversation_history or []
        )
        
        logger.info(f"Appointment processed successfully for {request.phone_number}")
        return result
        
    except Exception as e:
        logger.error(f"Error processing appointment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/events")
async def get_calendar_events(request: CalendarRequest):
    """
    Calendar Reader Agent: Get events for a specific date
    """
    try:
        logger.info(f"Getting calendar events for {request.date} (phone: {request.phone_number})")
        
        result = calendar_processor.calendar_agents.get_calendar_events(
            request.date,
            request.phone_number
        )
        
        logger.info(f"Calendar events retrieved for {request.date}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting calendar events: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/create-event")
async def create_calendar_event(request: EventCreationRequest):
    """
    Calendar Event Creator Agent: Create a new calendar event
    """
    try:
        logger.info(f"Creating calendar event for {request.phone_number}")
        
        result = calendar_processor.calendar_agents.create_calendar_event(
            request.event_details,
            request.phone_number
        )
        
        logger.info(f"Calendar event created successfully for {request.phone_number}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating calendar event: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/calendar/check-availability")
async def check_availability(request: CalendarRequest):
    """
    Check availability for a date and propose alternatives if needed
    """
    try:
        logger.info(f"Checking availability for {request.date} (phone: {request.phone_number})")
        
        result = calendar_processor.calendar_agents.check_availability_and_propose(
            request.date,
            request.phone_number
        )
        
        logger.info(f"Availability checked for {request.date}")
        return result
        
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/calendar/context/{phone_number}")
async def get_appointment_context(phone_number: str):
    """
    Get current appointment context for a phone number
    """
    try:
        context = calendar_processor.calendar_agents.get_appointment_context(phone_number)
        return {"phone_number": phone_number, "context": context}
        
    except Exception as e:
        logger.error(f"Error getting appointment context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/calendar/context/{phone_number}")
async def clear_appointment_context(phone_number: str):
    """
    Clear appointment context for a phone number
    """
    try:
        calendar_processor.calendar_agents.clear_appointment_context(phone_number)
        return {"message": f"Appointment context cleared for {phone_number}"}
        
    except Exception as e:
        logger.error(f"Error clearing appointment context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Detailed health check"""
    try:
        # Test environment variables
        required_env_vars = [
            'GEMINI_API_KEY',
            'LINKED_ACCOUNT_OWNER_ID'
        ]
        
        # Check for either separate API keys or fallback
        api_key_vars = [
            'ACI_CALENDAR_READER_API_KEY',
            'ACI_EVENT_CREATOR_API_KEY',
            'ACI_API_KEY'  # Fallback
        ]
        
        missing_vars = [var for var in required_env_vars if not os.getenv(var)]
        
        # Check if at least one API key is set
        has_api_key = any(os.getenv(var) for var in api_key_vars)
        if not has_api_key:
            missing_vars.append('ACI_API_KEY (or separate Calendar Reader/Event Creator keys)')
        
        # Get API key status from calendar agents
        api_key_status = calendar_processor.calendar_agents.get_api_key_status()
        
        health_status = {
            "status": "healthy" if not missing_vars else "unhealthy",
            "service": "Blue Collar Buddy API",
            "missing_environment_variables": missing_vars,
            "api_key_status": api_key_status,
            "endpoints": {
                "general_messages": "/process-message",
                "appointment_messages": "/process-appointment",
                "calendar_events": "/calendar/events",
                "create_event": "/calendar/create-event",
                "check_availability": "/calendar/check-availability",
                "appointment_context": "/calendar/context/{phone_number}"
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {"status": "unhealthy", "error": str(e)}

@app.get("/api-keys/status")
async def get_api_key_status():
    """
    Get API key status for debugging
    """
    try:
        status = calendar_processor.calendar_agents.get_api_key_status()
        return {
            "api_key_status": status,
            "recommendation": "Use separate API keys for better security and control"
        }
        
    except Exception as e:
        logger.error(f"API key status check failed: {e}")
        return {"error": str(e)}

@app.post("/update-settings")
async def update_settings(request: SettingsUpdate):
    """Update Bob's account and agent settings"""
    global bob_account, agent_settings
    
    try:
        if request.bobAccount is not None:
            bob_account = request.bobAccount
            print(f"Updated Bob's account settings: {bob_account}")
        
        if request.agentSettings is not None:
            agent_settings = request.agentSettings
            print(f"Updated agent settings: {agent_settings}")
        
        return {"message": "Settings updated successfully"}
        
    except Exception as e:
        print(f"Error updating settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/settings")
async def get_settings():
    """Get current settings"""
    return {
        "bobAccount": bob_account,
        "agentSettings": agent_settings
    }

@app.get("/conversations")
async def get_conversations():
    """Get all conversation histories"""
    return conversation_history

@app.get("/conversations/{phone_number}")
async def get_conversation(phone_number: str):
    """Get conversation history for a specific phone number"""
    return {
        "phone_number": phone_number,
        "history": conversation_history.get(phone_number, [])
    }

@app.delete("/conversations/{phone_number}")
async def clear_conversation(phone_number: str):
    """Clear conversation history for a specific phone number"""
    if phone_number in conversation_history:
        del conversation_history[phone_number]
    return {"message": "Conversation cleared"}

@app.post("/generate-prompt")
async def generate_prompt(request: MessageRequest):
    """Generate a prompt using Bob's settings"""
    try:
        # Create enhanced prompt with Bob's settings
        prompt = create_enhanced_prompt(request.message, request.phone_number)
        
        return {
            "prompt": prompt,
            "bob_account": bob_account,
            "agent_settings": agent_settings
        }
        
    except Exception as e:
        print(f"Error generating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def create_enhanced_prompt(message: str, phone_number: str) -> str:
    """Create an enhanced prompt using Bob's account and agent settings"""
    
    # Base prompt
    prompt = f"""
You are Bob, a friendly beehive builder and consultant. You help people with beehive construction, maintenance, and beekeeping advice.

CURRENT CONTEXT (for date/time grounding):
- Today is {datetime.now().strftime('%A, %B %d, %Y')}
- Current time is {datetime.now().strftime('%H:%M')} (24-hour format)
- Current year is {datetime.now().strftime('%Y')}

USER MESSAGE: {message}
"""
    
    # Add Bob's account information if available
    if bob_account:
        prompt += f"""

BOB'S PROFILE:
- Name: {bob_account.get('name', 'Bob')}
- Role: {bob_account.get('role', 'Beehive Builder & Consultant')}
- Profile: {bob_account.get('profile', 'Experienced beehive builder and consultant')}
- Location: {bob_account.get('location', 'UK')}
"""
        
        # Add services information
        services_type = bob_account.get('servicesType', 'none')
        if services_type == 'pricing':
            services = bob_account.get('services', [])
            if services:
                prompt += "\nSERVICES AND PRICING:\n"
                for service in services:
                    if service.get('name'):
                        price = service.get('price', 0)
                        prompt += f"- {service['name']}: £{price}\n"
        elif services_type == 'list':
            services = bob_account.get('services', [])
            if services:
                prompt += "\nSERVICES PROVIDED:\n"
                for service in services:
                    if service.get('name'):
                        prompt += f"- {service['name']}\n"
        elif services_type == 'none':
            prompt += "\nSERVICES: Discussed individually with clients (no fixed pricing)\n"
        
        # Add services not provided
        services_not_provided = bob_account.get('servicesNotProvided', '')
        if services_not_provided:
            prompt += f"\nSERVICES NOT PROVIDED: {services_not_provided}\n"
    
    # Add agent settings
    if agent_settings:
        prompt += f"""

AGENT SETTINGS:
- Enabled: {agent_settings.get('enabled', True)}
- Delay Time: {agent_settings.get('delayTime', 5)} seconds
- Default Greeting: {agent_settings.get('defaultGreeting', '')}
"""
    
    # Add instructions
    prompt += """

INSTRUCTIONS:
1. Always use absolute dates (YYYY-MM-DD) and times (HH:MM 24-hour format) when discussing appointments
2. If the user mentions relative times like "tomorrow" or "next Monday", convert them to absolute dates
3. For appointment scheduling, you need ALL of these details:
   - Client's full name
   - Exact date (YYYY-MM-DD format)
   - Exact time (HH:MM 24-hour format)
   - Complete location/address with postcode
4. If any details are missing, ask the user to provide them
5. Default appointment duration is 1 hour
6. Once all details are confirmed, create the appointment in Google Calendar
7. Be friendly and professional, always confirming details clearly
8. If services type is 'none' and user asks about pricing, respond with "PAUSE" to allow Bob to intervene
9. Use Bob's profile and services information to provide personalized responses

Respond naturally as Bob, helping with beehive-related questions or gathering appointment details.
"""
    
    return prompt

if __name__ == "__main__":
    # Check required environment variables
    required_vars = ['GEMINI_API_KEY', 'ACI_API_KEY', 'LINKED_ACCOUNT_OWNER_ID']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("Some features may not work properly")
    
    # Run the server
    port = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 