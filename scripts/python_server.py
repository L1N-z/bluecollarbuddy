import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from gemini_message_processor import GeminiMessageProcessor

# Initialize FastAPI app
app = FastAPI(title="WhatsApp AI Processor", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the message processor
processor = GeminiMessageProcessor()

class MessageRequest(BaseModel):
    message: str
    phone_number: str

class MessageResponse(BaseModel):
    response: str
    is_greeting: bool
    timestamp: str
    phone_number: str

@app.post("/process-message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process incoming WhatsApp messages using the Gemini AI processor
    """
    try:
        print(f"[DEBUG] Processing message from {request.phone_number}: {request.message}")
        
        # Process the message using the existing GeminiMessageProcessor
        result = processor.process_message(request.message, request.phone_number)
        
        print(f"[DEBUG] Response for {request.phone_number}: {result['response']}")
        
        return MessageResponse(**result)
        
    except Exception as e:
        print(f"[ERROR] Failed to process message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "WhatsApp AI Processor"}

@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "WhatsApp AI Processor API",
        "version": "1.0.0",
        "endpoints": {
            "process_message": "/process-message",
            "health": "/health"
        }
    }

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PYTHON_SERVER_PORT", "8000"))
    
    print(f"Starting WhatsApp AI Processor server on port {port}")
    print(f"Make sure GEMINI_API_KEY is set in your environment")
    
    uvicorn.run(
        "python_server:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 