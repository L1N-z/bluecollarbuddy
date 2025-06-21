# ACI.dev Calendar Integration Setup Guide

This guide will help you set up the ACI.dev calendar integration for the Blue Collar Buddy WhatsApp agent.

## Prerequisites

1. **ACI.dev Account**: Sign up at [ACI.dev](https://aci.dev)
2. **Calendar App**: Configure a calendar app (Google Calendar, Outlook, etc.) in ACI.dev
3. **API Keys**: Get your ACI API key and set up linked accounts

## Step 1: ACI.dev Platform Setup

### 1.1 Create ACI Account
1. Go to [ACI.dev](https://aci.dev) and sign up
2. Complete your profile setup

### 1.2 Configure Calendar App
1. In your ACI dashboard, go to "Apps"
2. Search for and add a calendar app (Google Calendar recommended)
3. Follow the OAuth2 flow to link your calendar account
4. Note your `LINKED_ACCOUNT_OWNER_ID` (found in the linked account details)

### 1.3 Get API Key
1. Go to "API Keys" in your ACI dashboard
2. Create a new API key
3. Copy the key for use in environment variables

## Step 2: Environment Variables

Add these environment variables to your deployment:

### For Vercel (Next.js Frontend)
```bash
ACI_API_KEY=your_aci_api_key_here
LINKED_ACCOUNT_OWNER_ID=your_linked_account_owner_id_here
PYTHON_SERVER_URL=https://your-python-server-url.onrender.com
```

### For Render (Python Backend)
```bash
ACI_API_KEY=your_aci_api_key_here
LINKED_ACCOUNT_OWNER_ID=your_linked_account_owner_id_here
GEMINI_API_KEY=your_gemini_api_key_here
```

## Step 3: Calendar App Configuration

### 3.1 Google Calendar Setup (Recommended)
1. In ACI.dev, add the Google Calendar app
2. Complete OAuth2 authorization
3. Grant permissions for:
   - Read calendar events
   - Create calendar events
   - Modify calendar events

### 3.2 Alternative Calendar Apps
- **Outlook Calendar**: Similar OAuth2 setup
- **Apple Calendar**: May require different authentication
- **Other calendars**: Check ACI.dev documentation for specific setup

## Step 4: Testing the Integration

### 4.1 Test Calendar Reader
```bash
curl -X POST https://your-python-server-url.onrender.com/calendar/events \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-01-22",
    "phone_number": "+1234567890"
  }'
```

### 4.2 Test Calendar Event Creation
```bash
curl -X POST https://your-python-server-url.onrender.com/calendar/create-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_details": {
      "title": "Test Beehive Consultation",
      "date": "2025-01-22",
      "time": "2:00 PM",
      "location": "Test Location"
    },
    "phone_number": "+1234567890"
  }'
```

### 4.3 Test Appointment Processing
```bash
curl -X POST https://your-python-server-url.onrender.com/process-appointment \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi Bob, I want to schedule a consultation for tomorrow at 2 PM at my house",
    "phone_number": "+1234567890"
  }'
```

## Step 5: WhatsApp Integration Testing

### 5.1 Test Appointment Flow
Send these messages to your WhatsApp number:

1. **Initial Request**: "Hi Bob, I'd like to schedule a beehive consultation"
2. **Date Proposal**: "How about tomorrow at 2 PM?"
3. **Location**: "At my house"
4. **Confirmation**: "Yes, that works for me"

### 5.2 Expected Flow
1. Bob responds asking for details
2. Bob checks calendar availability
3. Bob confirms appointment details
4. Bob creates calendar event
5. Bob asks for final confirmation
6. Bob sends "Great, see you then! 🐝"

## Step 6: Troubleshooting

### 6.1 Common Issues

**ACI API Key Issues**
```bash
# Check if API key is valid
curl -H "Authorization: Bearer YOUR_ACI_API_KEY" \
  https://api.aci.dev/v1/functions/search
```

**Calendar Permission Issues**
- Ensure calendar app has proper permissions
- Check linked account owner ID is correct
- Verify OAuth2 flow completed successfully

**Python Server Issues**
```bash
# Check server health
curl https://your-python-server-url.onrender.com/health
```

### 6.2 Debug Logs
Check the Python server logs for detailed error messages:
- ACI function search results
- Calendar event creation status
- Appointment context updates

### 6.3 Environment Variable Verification
```bash
# Test environment variables are loaded
curl https://your-python-server-url.onrender.com/health
```

## Step 7: Advanced Configuration

### 7.1 Custom Calendar Functions
You can extend the calendar functionality by:
1. Adding custom ACI functions
2. Modifying the appointment extraction logic
3. Customizing the confirmation flow

### 7.2 Multiple Calendar Support
To support multiple calendars:
1. Add multiple calendar apps in ACI.dev
2. Modify the calendar agents to handle multiple accounts
3. Add calendar selection logic

### 7.3 Timezone Handling
For proper timezone support:
1. Ensure calendar events include timezone information
2. Handle timezone conversions in appointment processing
3. Consider user's local timezone

## Step 8: Production Deployment

### 8.1 Security Considerations
- Use environment variables for all API keys
- Enable HTTPS for all endpoints
- Implement rate limiting
- Monitor API usage

### 8.2 Monitoring
- Set up logging for appointment flows
- Monitor calendar API usage
- Track successful/failed appointments
- Set up alerts for errors

### 8.3 Backup Strategy
- Consider backup calendar integration
- Implement fallback responses
- Store appointment data locally if needed

## Support

If you encounter issues:
1. Check the ACI.dev documentation
2. Review the Python server logs
3. Test individual components
4. Contact ACI.dev support for platform issues

## Next Steps

Once the calendar integration is working:
1. Test with real users
2. Gather feedback on appointment flow
3. Optimize response times
4. Add additional calendar features as needed 