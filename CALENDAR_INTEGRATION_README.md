# Calendar Integration for Blue Collar Buddy

This document explains the calendar integration features that allow Bob (the beehive consultant) to schedule appointments with customers via WhatsApp.

## 🗓️ Features Overview

### Calendar Reader Agent
- **Purpose**: Checks calendar availability for specific dates
- **Functionality**: 
  - Returns list of events with details (title, time, location)
  - Returns empty list if no events found
  - Handles date parsing and validation

### Calendar Event Creator Agent
- **Purpose**: Creates new calendar events when appointments are confirmed
- **Functionality**:
  - Creates events with title, date, time, location, and description
  - Integrates with ACI.dev calendar apps (Google Calendar, Outlook, etc.)
  - Handles appointment confirmation flow

## 🔄 Appointment Scheduling Flow

### 1. Initial Request
**User**: "Hi Bob, I'd like to schedule a beehive consultation"

**Bob**: "Great! I'd be happy to help you with your beehive consultation. When would you like to meet? I can help you with hive construction, colony management, honey extraction, and more."

### 2. Date/Time Proposal
**User**: "How about tomorrow at 2 PM?"

**Bob**: "Let me check my calendar for tomorrow..."

*[Calendar Reader checks availability]*

**Bob**: "Perfect! I'm free tomorrow at 2 PM. Where would you like to meet?"

### 3. Location Confirmation
**User**: "At my house"

**Bob**: "Great! I've scheduled our beehive consultation:

📅 Date: 2025-01-22
⏰ Time: 2:00 PM
📍 Location: At my house

Please confirm if these details work for you, and I'll see you there! 🐝"

### 4. Final Confirmation
**User**: "Yes, that works for me"

**Bob**: "Great, see you then! 🐝"

## 🛠️ Technical Implementation

### ACI.dev Integration
The calendar functionality uses [ACI.dev](https://aci.dev) to connect to calendar services:

```python
# Calendar Reader Agent
def get_calendar_events(self, date: str, phone_number: str) -> Dict[str, Any]:
    # Search for calendar functions
    search_result = self.aci.search_functions(
        query="calendar events list read",
        linked_account_owner_id=self.linked_account_owner_id
    )
    
    # Execute calendar read function
    execute_result = self.aci.execute_function(
        function_name=calendar_function['name'],
        arguments={"date": date, "linked_account_owner_id": self.linked_account_owner_id}
    )
```

### Appointment Context Management
The system maintains conversation context to track appointment details:

```python
# Store appointment context per phone number
appointment_context = {
    "proposed_date": "2025-01-22",
    "proposed_time": "2:00 PM", 
    "proposed_location": "At my house",
    "pending_confirmation": True,
    "event_id": "calendar_event_id"
}
```

### Message Processing Logic
The system intelligently routes messages:

1. **Appointment Detection**: Checks for appointment-related keywords
2. **Date/Time/Location Extraction**: Uses regex patterns to extract details
3. **Context Awareness**: Maintains conversation state across messages
4. **Calendar Integration**: Checks availability and creates events

## 📱 WhatsApp Integration

### Message Flow
1. **Webhook Reception**: Twilio sends webhook to `/api/webhook`
2. **Message Processing**: Routes to appropriate processor (general vs appointment)
3. **Context Management**: Maintains conversation history
4. **Response Generation**: Uses Gemini AI for natural responses
5. **Message Sending**: Sends response via Twilio WhatsApp API

### Conversation History
The system maintains conversation history to provide context:

```typescript
const conversationHistory: { 
  [phoneNumber: string]: Array<{
    role: 'user' | 'assistant', 
    content: string, 
    timestamp: Date 
  }> 
} = {};
```

## 🔧 Setup Requirements

### Environment Variables
```bash
# ACI.dev Integration
ACI_API_KEY=your_aci_api_key
LINKED_ACCOUNT_OWNER_ID=your_linked_account_owner_id

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# Twilio WhatsApp
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_whatsapp_number

# Server URLs
PYTHON_SERVER_URL=https://your-python-server.onrender.com
NEXT_PUBLIC_APP_URL=https://your-vercel-app.vercel.app
```

### ACI.dev Calendar App Setup
1. **Add Calendar App**: Configure Google Calendar or Outlook in ACI.dev
2. **OAuth2 Authorization**: Complete the authorization flow
3. **Permissions**: Grant read/write calendar permissions
4. **Linked Account**: Note the `LINKED_ACCOUNT_OWNER_ID`

## 🧪 Testing

### Test Calendar Reader
```bash
curl -X POST https://your-python-server.onrender.com/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-22",
    "phone_number": "+1234567890"
  }'
```

### Test Appointment Processing
```bash
curl -X POST https://your-python-server.onrender.com/process-appointment \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi Bob, I want to schedule a consultation for tomorrow at 2 PM at my house",
    "phone_number": "+1234567890"
  }'
```

### Test Full Integration
```bash
python scripts/test_aci_integration.py
```

## 📊 API Endpoints

### Python Server Endpoints
- `POST /process-message` - General message processing
- `POST /process-appointment` - Appointment-specific processing
- `POST /calendar/events` - Get calendar events for a date
- `POST /calendar/create-event` - Create new calendar event
- `POST /calendar/check-availability` - Check availability and propose alternatives
- `GET /calendar/context/{phone_number}` - Get appointment context
- `DELETE /calendar/context/{phone_number}` - Clear appointment context
- `GET /health` - Health check with environment variable status

### Next.js API Routes
- `POST /api/webhook` - Twilio WhatsApp webhook
- `POST /api/process-message` - Message processing with conversation history
- `POST /api/send-message` - Send WhatsApp messages

## 🔍 Debugging

### Logs to Monitor
1. **ACI Function Calls**: Check if calendar functions are found and executed
2. **Appointment Context**: Verify context is being maintained correctly
3. **Message Routing**: Ensure messages are routed to correct processor
4. **Calendar Integration**: Monitor event creation and availability checks

### Common Issues
1. **ACI API Key**: Ensure API key is valid and has proper permissions
2. **Calendar Permissions**: Verify calendar app has read/write access
3. **Linked Account ID**: Check that the linked account owner ID is correct
4. **Date Formats**: Ensure dates are in YYYY-MM-DD format
5. **Phone Number Format**: Verify phone numbers are properly formatted

## 🚀 Deployment

### Vercel (Next.js Frontend)
1. Set environment variables in Vercel dashboard
2. Deploy the Next.js application
3. Update Twilio webhook URL to point to Vercel deployment

### Render (Python Backend)
1. Set environment variables in Render dashboard
2. Deploy the Python server
3. Update `PYTHON_SERVER_URL` in Vercel environment variables

### Testing Deployment
1. Test webhook endpoint: `GET /api/webhook`
2. Test message processing: Send WhatsApp message
3. Test appointment flow: Try scheduling an appointment
4. Verify calendar integration: Check if events are created

## 📈 Future Enhancements

### Planned Features
1. **Multiple Calendar Support**: Handle multiple calendar accounts
2. **Timezone Handling**: Proper timezone conversion and display
3. **Recurring Appointments**: Support for recurring consultation schedules
4. **Calendar Sync**: Real-time calendar synchronization
5. **Appointment Reminders**: Automated reminder messages
6. **Rescheduling**: Allow users to reschedule appointments
7. **Cancellation**: Handle appointment cancellations

### Advanced Features
1. **Natural Language Processing**: Better date/time extraction
2. **Calendar Analytics**: Track appointment patterns and availability
3. **Integration APIs**: Connect with other scheduling systems
4. **Multi-language Support**: Support for different languages
5. **Voice Integration**: Voice-based appointment scheduling

## 📞 Support

For issues with:
- **ACI.dev Integration**: Check [ACI.dev documentation](https://aci.dev/docs)
- **Calendar Apps**: Verify OAuth2 setup and permissions
- **WhatsApp Integration**: Check Twilio logs and webhook configuration
- **Python Server**: Review server logs and environment variables

## 🎯 Success Metrics

Track these metrics to measure success:
1. **Appointment Success Rate**: % of appointment requests that result in confirmed events
2. **Response Time**: Time from message receipt to response
3. **User Satisfaction**: Feedback on appointment scheduling experience
4. **Calendar Integration Uptime**: % of successful calendar operations
5. **Error Rate**: % of failed appointment scheduling attempts 