import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai
import json
from datetime import datetime

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

# Initialize Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Store conversation histories
conversation_histories = {}

class MessageRequest(BaseModel):
    message: str
    phone_number: str

class MessageResponse(BaseModel):
    response: str
    is_greeting: bool
    timestamp: str
    phone_number: str

def is_greeting(message: str) -> bool:
    """Check if the message is a greeting"""
    greeting_words = [
        'hello', 'hi', 'hey', 'good morning', 'good afternoon', 
        'good evening', 'greetings', 'howdy', 'what\'s up', 'sup'
    ]
    
    message_lower = message.lower().strip()
    
    # Check if message starts with or contains greeting words
    for greeting in greeting_words:
        if message_lower.startswith(greeting) or greeting in message_lower:
            # Make sure it's not part of a larger sentence about something else
            if len(message_lower.split()) <= 3:  # Short messages are likely greetings
                return True
            # Check if greeting is at the beginning
            if message_lower.startswith(greeting):
                return True
    
    return False

def get_greeting_response() -> str:
    """Return a predefined greeting response from Bob"""
    import random
    greetings = [
        "Hey there! Bob here, your friendly neighborhood beehive builder. How can I help you today?",
        "Hi! This is Bob from Bob's Beehive Building. What can I do for you?",
        "Hello! Bob speaking - I build custom beehives and help folks with all their bee-related needs. What's on your mind?",
        "Hey! Bob here. I'm all about helping people with their beekeeping projects. What brings you my way today?"
    ]
    return random.choice(greetings)

def get_conversation_history(phone_number: str) -> list:
    """Get conversation history for a phone number"""
    return conversation_histories.get(phone_number, [])

def update_conversation_history(phone_number: str, user_message: str, bot_response: str):
    """Update conversation history"""
    if phone_number not in conversation_histories:
        conversation_histories[phone_number] = []
    
    # Add user message and bot response
    conversation_histories[phone_number].extend([
        {"role": "user", "content": user_message},
        {"role": "assistant", "content": bot_response}
    ])
    
    # Keep only last 20 messages to manage context size
    if len(conversation_histories[phone_number]) > 20:
        conversation_histories[phone_number] = conversation_histories[phone_number][-20:]

def extract_response_from_quotes(llm_output: str) -> str:
    """Extract response from double quotes in LLM output"""
    import re
    # Look for text within double quotes
    quote_pattern = r'"([^"]*)"'
    matches = re.findall(quote_pattern, llm_output)
    
    if matches:
        # Return the first quoted text found
        extracted = matches[0].strip()
        print(f"[DEBUG] Extracted response from quotes: {extracted}")
        return extracted
    else:
        # If no quotes found, return the whole response but log it
        print(f"[DEBUG] No quotes found in LLM output, using full response: {llm_output}")
        return llm_output.strip()

def process_with_gemini(message: str, phone_number: str) -> str:
    """Process message with Gemini AI"""
    try:
        # Get conversation history
        history = get_conversation_history(phone_number)
        
        # Bob's persona and business context
        bob_persona = """
You are Bob, a friendly and experienced beehive builder who runs a small beehive construction business called "Bob's Beehive Building". 

BUSINESS CONTEXT:
- You build custom beehives, repair existing ones, and provide beekeeping consultation
- You serve the local area and can travel within a reasonable distance (about 50 miles)
- You're knowledgeable about different hive types (Langstroth, Top Bar, Warre, Flow Hive, etc.)
- You care about bee health and sustainable beekeeping practices
- You offer services like: custom hive construction, repairs, consultations, inspections, equipment recommendations

CONVERSATION FLOW YOU SHOULD FOLLOW:
1. Initial Contact & Greeting → Welcome customers warmly
2. Issue Discovery → Ask about their beekeeping needs, experience level, hive preferences
3. Address Collection → Get their location to confirm you can service their area
4. Scheduling → Propose meeting times for consultation or work
5. Confirmation & Wrap-up → Confirm details and next steps

PERSONALITY TRAITS:
- Friendly, approachable, and enthusiastic about bees and beekeeping
- Professional but not overly formal - like talking to a neighbor
- Ask follow-up questions to understand their specific needs
- Share relevant tips or insights when appropriate
- Keep responses conversational and concise (2-4 sentences typically)
- Use first person - you ARE Bob, don't refer to yourself in third person

IMPORTANT GUIDELINES:
- Always respond as Bob in first person
- Never mention that you're an AI or language model
- If asked about specific pricing, explain you prefer to discuss after understanding their needs
- If they're outside your service area, politely explain and offer general advice
- Be helpful and try to guide the conversation toward understanding their beekeeping needs
- Show genuine interest in their beekeeping journey

Your response should be natural, helpful, and move the conversation forward toward scheduling a consultation or providing the help they need.
"""

        conversation_history = ""
        if history:
            conversation_history = "\n".join([
                f"{msg['role'].title()}: {msg['content']}" for msg in history
            ])
        else:
            conversation_history = "No previous conversation history."

        system_prompt = f"""
{bob_persona}

CONVERSATION HISTORY:
{conversation_history}

CURRENT MESSAGE TO RESPOND TO:
"{message}"

INSTRUCTIONS:
Please respond as Bob to the current message. Consider the conversation history to maintain context and continuity. 

IMPORTANT: Your entire response should be enclosed in double quotation marks like this: "Your response here"

Respond naturally as Bob would, keeping in mind the conversation flow and your role as a beehive builder.
"""

        print(f"[DEBUG] Sending to Gemini for {phone_number}")
        response = model.generate_content(system_prompt)
        llm_output = response.text
        
        print(f"[DEBUG] Raw LLM response for {phone_number}: {llm_output}")
        
        # Extract response from quotes
        extracted_response = extract_response_from_quotes(llm_output)
        
        print(f"[DEBUG] Extracted response for {phone_number}: {extracted_response}")
        
        return extracted_response
        
    except Exception as e:
        print(f"[ERROR] Gemini processing error: {e}")
        return "Hey, this is Bob! I'm having a bit of trouble with my system right now, but I'd love to help you with your beehive needs. Could you try sending your message again in a moment?"

@app.post("/process-message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    """
    Process incoming WhatsApp messages using the Gemini AI processor
    """
    try:
        print(f"[DEBUG] Processing message from {request.phone_number}: {request.message}")
        
        # Check if it's a greeting
        if is_greeting(request.message):
            print(f"[DEBUG] Detected greeting message")
            response = get_greeting_response()
            print(f"[DEBUG] Greeting response: {response}")
        else:
            print(f"[DEBUG] Non-greeting message, sending to Gemini")
            response = process_with_gemini(request.message, request.phone_number)
        
        # Update conversation history
        update_conversation_history(request.phone_number, request.message, response)
        
        result = {
            'response': response,
            'is_greeting': is_greeting(request.message),
            'timestamp': datetime.now().isoformat(),
            'phone_number': request.phone_number
        }
        
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
        "python_server_simple:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 