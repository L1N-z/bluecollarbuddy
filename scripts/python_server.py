import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json
import logging

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
        logger.info(f"Processing message for {request.phone_number}: {request.message[:50]}...")
        
        result = gemini_processor.process_message(
            request.message,
            request.phone_number,
            request.conversation_history or []
        )
        
        logger.info(f"Message processed successfully for {request.phone_number}")
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