# Weather Marketplace

A multi-agent weather advisory system built with FetchAI's Agentverse, featuring three tiers of weather agents and a React frontend interface. The system provides weather information and recommendations with different levels of detail based on the selected service tier.

## Project Overview

The system consists of:

- **Budget Weather Agent** ($0.99/request)
  - Basic weather information
  - One recommendation per request
  - Port: 5009

- **Premium Weather Agent** ($1.99/request)
  - Detailed weather information
  - Two recommendations per request
  - Port: 5008

- **Luxury Weather Agent** ($2.99/request)
  - Comprehensive weather information
  - One recommendation and a date idea
  - Port: 5006

- **Frontend Client Agent**
  - Handles communication between UI and weather agents
  - Manages agent discovery and response handling
  - Port: 5001

- **React Frontend**
  - Modern, responsive UI
  - Real-time agent discovery
  - Interactive chat interface
  - Port: 3000

## Prerequisites

- Python 3.12+
- Node.js and npm
- FetchAI Agentverse account and API key
- Anthropic API key for Claude AI

## Project Structure

```
project/
├── backend/
│   ├── budget_weather.py
│   ├── premium_weather.py
│   ├── luxury_weather.py
│   ├── client_agent.py
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── TravelAdvisor.js
│   │   └── ...
│   └── package.json
└── README.md
```

## Environment Setup

1. Create a `.env` file in the backend directory with:
```
AGENTVERSE_API_KEY=your_agentverse_key
WEATHER_KEY1=your_budget_agent_key
WEATHER_KEY2=your_premium_agent_key
WEATHER_KEY3=your_luxury_agent_key
CLIENT_KEY3=your_client_agent_key
ANTHROPIC_API_KEY=your_anthropic_key
```

2. Install backend dependencies:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install fetchai langchain-anthropic flask flask-cors python-dotenv
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
```

## Running the System

1. Start the weather agents (in separate terminals):
```bash
# Terminal 1
python budget_weather.py

# Terminal 2
python premium_weather.py

# Terminal 3
python luxury_weather.py
```

2. Start the client agent:
```bash
# Terminal 4
python client_agent.py
```

3. Start the frontend:
```bash
# Terminal 5
cd frontend
npm start
```

The system will be accessible at:
- Frontend UI: http://localhost:3000
- Client Agent: http://localhost:5001
- Weather Agents: http://localhost:5006, 5008, 5009

## Using the System

1. Open the frontend application in your browser
2. Click "Find Travel Advisors" to discover available weather agents
3. Select your preferred weather service tier
4. Enter your location in the chat interface
5. Receive weather information and recommendations based on your selected tier

## Features

- **Multi-tier Service**: Choose from three levels of weather advisory services
- **Real-time Communication**: Asynchronous message handling
- **Responsive Design**: Mobile-friendly interface
- **Smart Recommendations**: AI-powered weather analysis and suggestions
- **Interactive Chat**: User-friendly chat interface with loading indicators
- **Error Handling**: Robust error management and user feedback

## System Architecture

### Overview
The system follows a microservices architecture with multiple agents communicating through RESTful APIs and webhooks. The system consists of three main components:

1. **Frontend Layer** (Port 3000)
   - React-based user interface
   - Components:
     - App.js (main component)
     - Search Input
     - Agent List
     - Weather Report display

2. **Backend Client** (Port 5001)
   - API Endpoints:
     - /api/search-agents
     - /api/get-weather
     - /api/webhook
     - /api/get-weather-response

3. **Weather Agents**
   - Budget Agent (Port 5003, $0.99)
   - Premium Agent (Port 5004, $1.99)
   - Luxury Agent (Port 5005, $2.99)

### Communication Flow
1. User initiates search for weather agents from frontend
2. Backend client queries AgentVerse using fetch.ai("weather")
3. Available agents are returned and displayed
4. User selects agent and requests weather information
5. Request is routed through backend client to selected weather agent
6. Weather agent processes request and returns response
7. Response is displayed in frontend interface

### Component Interaction
- Frontend communicates with backend client via HTTP requests
- Backend client discovers and communicates with weather agents through AgentVerse
- Weather agents are registered with AgentVerse and respond to requests via webhooks
- All agents use FetchAI's communication protocol for message passing

### Integration Points
- AgentVerse for agent discovery and registration
- Claude AI for weather analysis and recommendations
- FetchAI framework for agent communication
- Flask for REST API endpoints
- React for frontend user interface

## Technical Details

- **Backend**: Python with Flask and FetchAI's agent framework
- **Frontend**: React with Tailwind CSS
- **AI Integration**: Claude AI for natural language processing
- **Communication**: RESTful APIs and webhooks
- **State Management**: React hooks for frontend state
- **Styling**: Tailwind CSS for responsive design

## Error Handling

The system includes comprehensive error handling:
- API authentication failures
- Network timeouts
- Invalid locations
- Missing agent responses
- Frontend-backend communication issues

## Security

- Environment variables for sensitive keys
- CORS protection
- Input validation
- Error message sanitization

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
