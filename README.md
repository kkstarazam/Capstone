# Weather Intelligence Agent

An AI-powered mobile weather assistant that provides personalized weather insights, smart recommendations, and proactive alerts based on your schedule and preferences.

## Overview

This application combines weather intelligence with calendar awareness to help you plan your day. The AI agent doesn't just tell you the weather—it understands your schedule, remembers your preferences, and proactively helps you make better decisions.

## Features

### Intelligent Conversations
- Natural language weather queries via Letta-powered stateful agent
- Context-aware responses based on your schedule
- Personalized recommendations for activities and clothing
- Long-term memory for user preferences and patterns

### Calendar Integration
- Google Calendar integration for weather-aware scheduling
- Automatically checks weather for scheduled events
- Creates weather-based reminders (e.g., "bring umbrella")

### Proactive Weather Alerts
- Push notifications for severe weather warnings
- Rain alerts when precipitation is expected
- Temperature extreme notifications
- Schedule-aware weather updates

### Location Services
- Search any location worldwide
- Save favorite locations
- Automatic geocoding and reverse geocoding

## Tech Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Python 3.11+, FastAPI |
| **AI Agent** | Letta (stateful agent with memory) |
| **Weather Data** | Open-Meteo API (free, no key required) |
| **Geocoding** | Nominatim/OpenStreetMap (free) |
| **Calendar** | Google Calendar API |
| **Mobile App** | Flutter (iOS & Android) |
| **Push Notifications** | Firebase Cloud Messaging |

## Project Structure

```
weather-intelligence-agent/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── agent/             # Letta agent configuration
│   │   ├── api/               # REST API endpoints
│   │   ├── models/            # Pydantic schemas
│   │   ├── services/          # Notifications & alerts
│   │   └── tools/             # Weather, geocoding, calendar
│   ├── tests/                 # Unit and integration tests
│   ├── requirements.txt
│   └── run.py
│
└── mobile/                    # Flutter mobile app
    └── lib/
        ├── models/            # Data models
        ├── providers/         # State management
        ├── screens/           # UI screens
        ├── services/          # API & notifications
        └── widgets/           # Reusable components
```

## Installation

### Prerequisites

- Python 3.11 or higher
- Flutter 3.0 or higher
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/liamstar97/cofi26-weather-agent.git
   cd cofi26-weather-agent
   ```

2. **Create a virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your settings:
   ```env
   # Required for Letta agent
   OPENAI_API_KEY=your-openai-api-key

   # Optional: Google Calendar integration
   GOOGLE_CLIENT_ID=your-client-id
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

5. **Start the backend server**
   ```bash
   python run.py
   ```

   The API will be available at `http://localhost:8000`
   - API Documentation: `http://localhost:8000/docs`
   - Health Check: `http://localhost:8000/api/v1/health`

### Mobile App Setup

1. **Navigate to mobile directory**
   ```bash
   cd mobile
   ```

2. **Install Flutter dependencies**
   ```bash
   flutter pub get
   ```

3. **Configure API endpoint**

   Edit `lib/services/api_service.dart` and update the `baseUrl`:
   ```dart
   static const String baseUrl = 'http://YOUR_BACKEND_IP:8000/api/v1';
   ```

4. **Run the app**
   ```bash
   # For development
   flutter run

   # For iOS
   flutter run -d ios

   # For Android
   flutter run -d android
   ```

### Optional: Google Calendar Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Google Calendar API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` and place it in the `backend/` directory
6. Add your client ID and secret to `.env`

### Optional: Firebase Push Notifications

1. Create a [Firebase project](https://console.firebase.google.com/)
2. Add your iOS and Android apps
3. Download configuration files:
   - `google-services.json` for Android
   - `GoogleService-Info.plist` for iOS
4. Place them in the appropriate mobile app directories

## Usage

### API Endpoints

#### Chat with Weather Agent
```bash
curl -X POST "http://localhost:8000/api/v1/chat" \
  -H "Content-Type: application/json" \
  -d '{"user_id": "user123", "message": "What is the weather in New York?"}'
```

#### Get Current Weather
```bash
curl -X POST "http://localhost:8000/api/v1/weather/current" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060}'
```

#### Get Weather Forecast
```bash
curl -X POST "http://localhost:8000/api/v1/weather/forecast?days=7" \
  -H "Content-Type: application/json" \
  -d '{"latitude": 40.7128, "longitude": -74.0060}'
```

#### Search Location
```bash
curl -X POST "http://localhost:8000/api/v1/geocode" \
  -H "Content-Type: application/json" \
  -d '{"query": "San Francisco, CA", "limit": 5}'
```

#### Subscribe to Weather Alerts
```bash
curl -X POST "http://localhost:8000/api/v1/alerts/subscribe?user_id=user123&latitude=40.7128&longitude=-74.0060&location_name=New%20York"
```

### Mobile App Features

1. **Home Screen**: View current weather and 7-day forecast
2. **Chat Screen**: Ask natural language weather questions
3. **Location Search**: Find and save favorite locations
4. **Settings**: Toggle temperature units (°F/°C)

### Example Conversations

```
User: "What's my day looking like?"
Agent: "Good morning! It's currently 52°F and cloudy.
       You have a lunch meeting at noon—perfect timing as
       it'll be 65°F and sunny by then."

User: "When should I go for a run this week?"
Agent: "Based on this week's forecast, I recommend:
       - Wednesday 6am: 58°F, clear skies
       - Saturday 8am: 68°F, sunny (best option!)"

User: "Will it rain today?"
Agent: "There's a 75% chance of rain starting around 3pm.
       I'd recommend bringing an umbrella if you're heading out!"
```

## Testing

### Run All Tests
```bash
cd backend
pytest -v
```

### Run Specific Test Files
```bash
# Service unit tests
pytest tests/test_services.py -v

# Mocked API tests
pytest tests/test_mocked_api.py -v

# Weather tool tests
pytest tests/test_weather.py -v
```

### Test Coverage
The test suite includes:
- 42 unit tests for services (notifications, alerts)
- Mocked API tests for weather and geocoding
- End-to-end integration tests
- Alert detection logic tests

## API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/chat` | POST | Send message to weather agent |
| `/api/v1/weather/current` | POST | Get current weather |
| `/api/v1/weather/forecast` | POST | Get daily forecast |
| `/api/v1/weather/hourly` | POST | Get hourly forecast |
| `/api/v1/geocode` | POST | Search for locations |
| `/api/v1/reverse-geocode` | POST | Get location from coordinates |
| `/api/v1/agent/create` | POST | Create weather agent for user |
| `/api/v1/alerts/subscribe` | POST | Subscribe to weather alerts |
| `/api/v1/notifications/register` | POST | Register device for push notifications |
| `/api/v1/health` | GET | API health check |

Full API documentation available at `http://localhost:8000/docs` when the server is running.

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes* | OpenAI API key for Letta agent |
| `DEBUG` | No | Enable debug mode (default: false) |
| `API_HOST` | No | API host (default: 0.0.0.0) |
| `API_PORT` | No | API port (default: 8000) |
| `GOOGLE_CLIENT_ID` | No | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | No | Google OAuth client secret |

*Required for Letta agent functionality

## Troubleshooting

### Backend won't start
- Ensure Python 3.11+ is installed: `python --version`
- Check all dependencies are installed: `pip install -r requirements.txt`
- Verify `.env` file exists with required variables

### Mobile app can't connect to backend
- Ensure backend is running: `curl http://localhost:8000/api/v1/health`
- Update `baseUrl` in `api_service.dart` with correct IP
- For physical devices, use your machine's local IP, not `localhost`

### Weather data not loading
- Open-Meteo API is free and doesn't require a key
- Check your internet connection
- Verify coordinates are valid (latitude: -90 to 90, longitude: -180 to 180)

### Calendar integration not working
- Ensure `credentials.json` is in the backend directory
- Complete OAuth flow by running the backend and authenticating
- Check that Google Calendar API is enabled in your Google Cloud project

## Future Enhancements

- Integration with smart home devices
- Photo recognition for weather condition verification
- Community weather reports and updates
- Travel itinerary weather tracking
- Health recommendations based on weather (air quality, UV index)
- Multi-user support for family or group planning

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Contributors

- kkstarazam

## Acknowledgments

- Built as part of an agentic application course project
- Weather data provided by [Open-Meteo](https://open-meteo.com/)
- Geocoding by [OpenStreetMap/Nominatim](https://nominatim.org/)
- Stateful agent powered by [Letta](https://www.letta.com/)
