# BizzyBuddy: AI-Powered WhatsApp Appointment Scheduler

BizzyBuddy is an intelligent WhatsApp agent designed for small business owners to automate appointment scheduling. It features a natural language interface for conversing with clients, a web-based dashboard for configuration, and seamless integration with Google Calendar.

## Key Features

- **Automated WhatsApp Conversations**: Engages with clients in a natural, human-like manner to understand their needs.
- **Intelligent Appointment Scheduling**: Checks for availability in your Google Calendar and books appointments directly.
- **Web Dashboard**: A central place to manage your account details, agent settings, and more.
- **Powered by Gemini & ACI**: Utilizes Google's Gemini for language processing and the ACI.dev SDK for robust agentic workflows.
- **Customizable**: Configure the agent's persona, services, and availability through the dashboard.
- **Scalable**: Built with a Next.js frontend and a separate Python (FastAPI) backend, ready for deployment.

## How It Works: A User Journey

A client sends a message, and BizzyBuddy takes over. The agent understands the request, checks for available slots, and confirms the appointment. Once confirmed, the event is automatically added to your Google Calendar.

### 1. The Conversation

The client initiates a conversation and requests an appointment.

| Initiating Contact                                     | Scheduling the Appointment                               |
| ------------------------------------------------------ | -------------------------------------------------------- |
| ![Conversation Start](./docs/images/conversation-1.png) | ![Conversation Booking](./docs/images/conversation-2.png) |

### 2. The Result: Automated Calendar Entry

The agent confirms the details and creates the event in Google Calendar without any manual intervention.

| Calendar Before                                        | Calendar After                                         |
| ------------------------------------------------------ | ------------------------------------------------------ |
| ![Calendar Before](./docs/images/calendar-before.png)   | ![Calendar After](./docs/images/calendar-after.png)     |

## Tech Stack

- **Frontend**: Next.js, React, Material-UI, Tailwind CSS
- **Backend**: Python, FastAPI, LangChain
- **AI & Agents**: Google Gemini, ACI.dev SDK
- **Database**: Supabase
- **Messaging**: Twilio WhatsApp API
- **Calendar**: Google Calendar API

## Getting Started

Refer to the `QUICK_START.md` for instructions on how to set up and run the project locally.
