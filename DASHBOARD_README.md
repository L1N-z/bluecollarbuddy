# 🐝 Bob's Beehive Dashboard

A comprehensive dashboard for Bob, the beehive builder and consultant, to manage his WhatsApp agent, account settings, and business operations.

## 🚀 Features

### 📊 Main Dashboard
- **Account Settings**: Manage Bob's profile, services, and business information
- **Agent Settings**: Control WhatsApp agent behavior and responses
- **Calendar**: View and manage appointments (Coming Soon)
- **WhatsApp Messages**: View conversation history (Coming Soon)

### 👤 Account Settings
- **Personal Information**: Name, role, role description, and profile
- **Services Configuration**: Three service types:
  - **Services and Pricing List**: Fixed pricing for services
  - **Services List**: Services without pricing
  - **Services Discussed/None**: Individual pricing discussions
- **Location**: UK postcode for service area
- **Services NOT Provided**: List of services Bob doesn't offer

### 🤖 Agent Settings
- **Enable/Disable**: Turn the WhatsApp agent on or off
- **Message Processing Delay**: Buffer time before processing messages (default: 5 seconds)
- **Default Greeting**: Custom greeting message for new conversations

## 🎨 Design

- **Color Scheme**: Light blue, green, and white (Google/WhatsApp inspired)
- **Framework**: Next.js with TypeScript
- **Styling**: Tailwind CSS with Material UI components
- **Animations**: Smooth transitions and hover effects

## 🛠️ Technical Architecture

### Frontend (Next.js)
```
app/
├── page.tsx                 # Main dashboard
├── api/
│   └── bob-settings/
│       └── route.ts        # Settings API endpoints
└── components/
    └── ui/                 # Reusable UI components
```

### Backend (Python FastAPI)
```
scripts/
├── python_server.py        # Main API server
├── gemini_calendar_processor.py  # LLM integration
├── robust_event_creator.py       # Event creation system
└── aci_calendar_agents.py        # Calendar integration
```

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+
- Required API keys (see Environment Variables)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd bluecollarbuddy
   ```

2. **Install frontend dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r scripts/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

5. **Start the development servers**

   **Terminal 1 - Frontend:**
   ```bash
   npm run dev
   ```

   **Terminal 2 - Backend:**
   ```bash
   python scripts/python_server.py
   ```

6. **Access the dashboard**
   - Open http://localhost:3000
   - Configure Bob's account and agent settings

## 🔧 Configuration

### Environment Variables

```env
# Twilio Configuration
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token

# Gemini AI
GEMINI_API_KEY=your_gemini_api_key

# ACI Calendar Integration
ACI_API_KEY=your_aci_api_key
ACI_CALENDAR_READER_API_KEY=your_calendar_reader_key
ACI_EVENT_CREATOR_API_KEY=your_event_creator_key
LINKED_ACCOUNT_OWNER_ID=your_linked_account_id

# Python Server
PYTHON_SERVER_URL=http://localhost:8000
```

### Bob's Account Setup

1. **Navigate to Account Settings**
2. **Fill in required fields:**
   - Name (required)
   - Profile (required)
   - Location/Postcode (required)

3. **Configure Services:**
   - Choose service type (pricing/list/none)
   - Add services with names and prices (if applicable)
   - List services not provided (optional)

4. **Save Account Settings**

### Agent Configuration

1. **Navigate to Agent Settings**
2. **Configure:**
   - Enable/disable agent
   - Set message processing delay
   - Add default greeting (optional)
3. **Save Agent Settings**

## 🔄 API Endpoints

### Frontend API (`/api/bob-settings`)

- `GET /api/bob-settings` - Get all settings
- `GET /api/bob-settings?type=account` - Get account settings
- `GET /api/bob-settings?type=agent` - Get agent settings
- `POST /api/bob-settings` - Update settings

### Backend API (`http://localhost:8000`)

- `GET /health` - Health check
- `POST /process-message` - Process WhatsApp messages
- `POST /update-settings` - Update Bob's settings
- `GET /settings` - Get current settings
- `GET /conversations` - Get conversation history
- `POST /generate-prompt` - Generate LLM prompts

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python scripts/test_dashboard.py
```

This will test:
- Dashboard accessibility
- Settings API functionality
- Python server integration
- Message processing

## 🔐 Security Features

- **Input Validation**: All form inputs are validated
- **Required Fields**: Mandatory fields are enforced
- **Error Handling**: Comprehensive error handling and user feedback
- **Data Persistence**: Settings are stored and synchronized between frontend and backend

## 🎯 Business Logic

### Service Types

1. **Services and Pricing List**
   - Fixed pricing for each service
   - Agent can quote prices directly
   - At least one service required

2. **Services List (No Pricing)**
   - Services listed without prices
   - Agent provides service information
   - Pricing discussed individually

3. **Services Discussed/None**
   - No fixed service list
   - Agent responds "PAUSE" for pricing questions
   - Bob intervenes for pricing discussions

### Message Processing

1. **Agent Enabled**: Normal message processing
2. **Agent Disabled**: Messages ignored, no responses sent
3. **Delay Processing**: Configurable buffer time before processing
4. **PAUSE Response**: Special handling for pricing discussions

## 📱 WhatsApp Integration

The dashboard integrates with the existing WhatsApp system:

- **Webhook**: Receives messages from Twilio
- **Processing**: Uses Bob's settings for personalized responses
- **Calendar**: Integrates with Google Calendar for appointments
- **History**: Maintains conversation history

## 🚀 Deployment

### Vercel Deployment
1. Connect repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Python Server Deployment
1. Deploy to Render, Railway, or similar platform
2. Update `PYTHON_SERVER_URL` environment variable
3. Ensure all API keys are configured

## 🔧 Troubleshooting

### Common Issues

1. **Dashboard not loading**
   - Check if Next.js server is running
   - Verify environment variables

2. **Settings not saving**
   - Check browser console for errors
   - Verify API endpoints are accessible

3. **Python server connection issues**
   - Ensure Python server is running on port 8000
   - Check `PYTHON_SERVER_URL` environment variable

4. **WhatsApp messages not processed**
   - Verify agent is enabled
   - Check Twilio webhook configuration
   - Review Python server logs

### Debug Mode

Enable debug logging:

```bash
# Frontend
DEBUG=* npm run dev

# Backend
python scripts/python_server.py --debug
```

## 📈 Future Enhancements

- [ ] Calendar integration with appointment management
- [ ] WhatsApp message history viewer
- [ ] Analytics and reporting dashboard
- [ ] Multi-language support
- [ ] Advanced scheduling features
- [ ] Customer database management
- [ ] Payment integration
- [ ] Mobile app version

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue on GitHub

---

**Bob's Beehive Dashboard** - Making beehive consultation management simple and efficient! 🐝 