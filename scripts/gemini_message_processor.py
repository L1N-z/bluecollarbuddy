import os
import json
import re
from datetime import datetime
from typing import Dict, List, Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

class GeminiMessageProcessor:
    def __init__(self):
        # Initialize Gemini with LangChain
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=os.getenv('GEMINI_API_KEY'),
            temperature=0.7
        )
        
        # Store conversation histories
        self.conversation_histories = {}
        
        # Bob's persona and business context
        self.bob_persona = """
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

    def is_greeting(self, message: str) -> bool:
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

    def get_greeting_response(self) -> str:
        """Return a predefined greeting response from Bob"""
        import random
        greetings = [
            "Hey there! Bob here, your friendly neighborhood beehive builder. How can I help you today?",
            "Hi! This is Bob from Bob's Beehive Building. What can I do for you?",
            "Hello! Bob speaking - I build custom beehives and help folks with all their bee-related needs. What's on your mind?",
            "Hey! Bob here. I'm all about helping people with their beekeeping projects. What brings you my way today?"
        ]
        return random.choice(greetings)

    def get_conversation_history(self, phone_number: str) -> List:
        """Get conversation history for a phone number"""
        return self.conversation_histories.get(phone_number, [])

    def update_conversation_history(self, phone_number: str, user_message: str, bot_response: str):
        """Update conversation history"""
        if phone_number not in self.conversation_histories:
            self.conversation_histories[phone_number] = []
        
        # Add user message and bot response
        self.conversation_histories[phone_number].extend([
            HumanMessage(content=user_message),
            AIMessage(content=bot_response)
        ])
        
        # Keep only last 20 messages to manage context size
        if len(self.conversation_histories[phone_number]) > 20:
            self.conversation_histories[phone_number] = self.conversation_histories[phone_number][-20:]

    def extract_response_from_quotes(self, llm_output: str) -> str:
        """Extract response from double quotes in LLM output"""
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

    def process_with_gemini(self, message: str, phone_number: str) -> str:
        """Process message with Gemini LLM using LangChain"""
        try:
            # Get conversation history
            history = self.get_conversation_history(phone_number)
            
            # Create the prompt
            system_prompt = f"""
{self.bob_persona}

CONVERSATION HISTORY:
{self.format_history_for_prompt(history)}

CURRENT MESSAGE TO RESPOND TO:
"{message}"

INSTRUCTIONS:
Please respond as Bob to the current message. Consider the conversation history to maintain context and continuity. 

IMPORTANT: Your entire response should be enclosed in double quotation marks like this: "Your response here"

Respond naturally as Bob would, keeping in mind the conversation flow and your role as a beehive builder.
"""

            print(f"[DEBUG] User message: {message}")
            print(f"[DEBUG] Phone number: {phone_number}")
            
            # Create messages for LangChain
            messages = [SystemMessage(content=system_prompt)]
            
            # Get response from Gemini
            response = self.llm.invoke(messages)
            llm_output = response.content
            
            print(f"[DEBUG] Raw LLM response: {llm_output}")
            
            # Extract response from quotes
            extracted_response = self.extract_response_from_quotes(llm_output)
            
            print(f"[DEBUG] Final extracted response: {extracted_response}")
            
            return extracted_response
            
        except Exception as e:
            print(f"[ERROR] Gemini processing error: {e}")
            return "Hey, this is Bob! I'm having a bit of trouble with my system right now, but I'd love to help you with your beehive needs. Could you try sending your message again in a moment?"

    def format_history_for_prompt(self, history: List) -> str:
        """Format conversation history for the prompt"""
        if not history:
            return "No previous conversation history."
        
        formatted = []
        for msg in history:
            if isinstance(msg, HumanMessage):
                formatted.append(f"Customer: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted.append(f"Bob: {msg.content}")
        
        return "\n".join(formatted)

    def process_message(self, message: str, phone_number: str) -> Dict[str, any]:
        """Main method to process incoming messages"""
        print(f"[DEBUG] Processing message from {phone_number}: {message}")
        
        # Check if it's a greeting
        if self.is_greeting(message):
            print(f"[DEBUG] Detected greeting message")
            response = self.get_greeting_response()
            print(f"[DEBUG] Greeting response: {response}")
        else:
            print(f"[DEBUG] Non-greeting message, sending to Gemini")
            response = self.process_with_gemini(message, phone_number)
        
        # Update conversation history
        self.update_conversation_history(phone_number, message, response)
        
        return {
            'response': response,
            'is_greeting': self.is_greeting(message),
            'timestamp': datetime.now().isoformat(),
            'phone_number': phone_number
        }

# Example usage and testing
if __name__ == "__main__":
    processor = GeminiMessageProcessor()
    
    # Test messages
    test_messages = [
        ("Hello!", "whatsapp:+1234567890"),
        ("I need help with building a beehive", "whatsapp:+1234567890"),
        ("I'm a beginner beekeeper", "whatsapp:+1234567890"),
        ("I'm located in Springfield", "whatsapp:+1234567890"),
        ("What types of hives do you recommend?", "whatsapp:+1234567890"),
        ("Hi there", "whatsapp:+1234567891"),  # Different number
        ("How much do your services cost?", "whatsapp:+1234567891")
    ]
    
    print("Testing Gemini Message Processor")
    print("=" * 50)
    
    for message, phone in test_messages:
        result = processor.process_message(message, phone)
        print(f"\n📱 From: {phone}")
        print(f"👤 User: {message}")
        print(f"🤖 Bob: {result['response']}")
        print(f"🏷️  Greeting: {result['is_greeting']}")
        print("-" * 30)
