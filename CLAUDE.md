# CLAUDE.md - AI Assistant Guide for Weather Intelligence Agent

This document provides essential context for AI assistants working on this codebase.

## Project Overview

**Weather Intelligence Agent** is an AI-powered mobile weather assistant combining:
- A Python FastAPI backend with Letta-based stateful AI agent
- A Flutter mobile application for iOS and Android
- Integration with free weather APIs, geocoding, and Google Calendar

The agent provides personalized weather insights, smart recommendations, and proactive alerts based on user schedules and preferences.

## Repository Structure

```
Capstone/
├── backend/                      # Python FastAPI backend
│   ├── app/
│   │   ├── agent/               # Letta agent configuration
│   │   │   └── weather_agent.py # Agent setup, system prompt, tools
│   │   ├── api/
│   │   │   └── routes.py        # All REST API endpoints (~310 lines)
│   │   ├── models/
│   │   │   └── schemas.py       # Pydantic request/response models
│   │   ├── services/
│   │   │   ├── notifications.py # Firebase FCM push notifications
│   │   │   └── weather_alerts.py # Alert monitoring & subscriptions
│   │   ├── tools/
│   │   │   ├── weather.py       # Open-Meteo API integration
│   │   │   ├── geocoding.py     # Nominatim/OSM geocoding
│   │   │   └── calendar.py      # Google Calendar OAuth 2.0
│   │   ├── config.py            # Pydantic settings from env vars
│   │   └── main.py              # FastAPI app initialization
│   ├── tests/                   # pytest test suite
│   │   ├── conftest.py          # Fixtures (async event loop)
│   │   ├── test_services.py     # Notification & alert tests (42+ tests)
│   │   ├── test_mocked_api.py   # Mocked external API tests
│   │   ├── test_weather.py      # Weather tool tests
│   │   ├── test_geocoding.py    # Geocoding tool tests
│   │   └── test_api_e2e.py      # End-to-end integration tests
│   ├── requirements.txt         # Python dependencies
│   ├── pytest.ini              # Test configuration
│   ├── run.py                  # Server startup script
│   └── .env.example            # Environment template
│
├── mobile/                      # Flutter mobile app
│   ├── lib/
│   │   ├── main.dart           # App entry with MultiProvider
│   │   ├── models/
│   │   │   ├── weather_models.dart  # Weather data classes
│   │   │   └── chat_models.dart     # Chat message models
│   │   ├── providers/
│   │   │   ├── weather_provider.dart # Weather state management
│   │   │   └── chat_provider.dart    # Chat state management
│   │   ├── screens/
│   │   │   ├── home_screen.dart           # Weather dashboard
│   │   │   ├── chat_screen.dart           # AI chat interface
│   │   │   └── location_search_screen.dart
│   │   ├── services/
│   │   │   ├── api_service.dart         # HTTP client for backend
│   │   │   └── notification_service.dart # FCM handling
│   │   └── widgets/
│   │       ├── weather_card.dart
│   │       ├── forecast_list.dart
│   │       └── chat_bubble.dart
│   └── pubspec.yaml            # Flutter dependencies
│
└── README.md                   # Project documentation
```

## Tech Stack

### Backend
| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | FastAPI 0.109+ | Async-first, OpenAPI docs |
| Server | Uvicorn | ASGI server |
| AI Agent | Letta 0.4+ | Stateful agent with memory |
| HTTP Client | httpx, aiohttp | Async HTTP requests |
| Validation | Pydantic 2.5+ | Request/response schemas |
| Testing | pytest, pytest-asyncio | Async test support |

### Mobile
| Component | Technology | Notes |
|-----------|------------|-------|
| Framework | Flutter 3.0+ | Cross-platform |
| Language | Dart 3.0+ | Null safety |
| State | Provider 6.1+ | ChangeNotifier pattern |
| HTTP | http, Dio | API communication |
| Notifications | Firebase Messaging | Push notifications |
| Location | geolocator, geocoding | Device location |

### External APIs (No keys required for core functionality)
- **Weather**: Open-Meteo API (free, open-source)
- **Geocoding**: Nominatim/OpenStreetMap (free)
- **Calendar**: Google Calendar API (requires OAuth 2.0 setup)
- **Push**: Firebase Cloud Messaging (optional)

## Development Commands

### Backend

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Run server (http://localhost:8000)
python run.py

# Run all tests
pytest

# Run specific test files
pytest tests/test_services.py -v
pytest tests/test_weather.py -v
pytest tests/test_mocked_api.py -v

# Run with coverage
pytest --cov=app tests/
```

### Mobile

```bash
# Setup
cd mobile
flutter pub get

# Run app
flutter run

# Run on specific device
flutter run -d ios
flutter run -d android

# Analyze code
flutter analyze

# Run tests
flutter test
```

## API Endpoints

All endpoints prefixed with `/api/v1/`. Documentation at `http://localhost:8000/docs`.

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/chat` | POST | Send message to AI agent |
| `/weather/current` | POST | Current weather (lat/lon body) |
| `/weather/forecast` | POST | Daily forecast (days param) |
| `/weather/hourly` | POST | Hourly forecast (hours param) |
| `/geocode` | POST | Search locations by name |
| `/reverse-geocode` | POST | Coordinates to place name |
| `/calendar/events` | GET | Get upcoming events |
| `/calendar/reminder` | POST | Create weather reminder |
| `/agent/create` | POST | Create agent for user |
| `/agent/{user_id}` | GET/DELETE | Get/delete user agent |
| `/alerts/subscribe` | POST | Subscribe to weather alerts |
| `/notifications/register` | POST | Register device token |
| `/health` | GET | Health check |

## Code Patterns & Conventions

### Backend Python

1. **Async/Await**: All API handlers and service methods are async
   ```python
   async def get_current_weather(latitude: float, longitude: float) -> dict:
   ```

2. **Type Hints**: Use throughout for parameters and returns
   ```python
   def _weather_code_to_description(code: Optional[int]) -> str:
   ```

3. **Pydantic Models**: For all request/response validation
   ```python
   class LocationRequest(BaseModel):
       latitude: float
       longitude: float
   ```

4. **Service Pattern**: Business logic in `/services/`, tools in `/tools/`
   ```python
   service = get_notification_service()
   result = await service.send_notification(user_id, title, body)
   ```

5. **Error Handling**: HTTPException with descriptive messages
   ```python
   except Exception as e:
       raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
   ```

6. **Docstrings**: Google-style for functions with Args/Returns sections

### Mobile Dart/Flutter

1. **Provider Pattern**: ChangeNotifier for state management
   ```dart
   class WeatherProvider extends ChangeNotifier {
     void setWeather(CurrentWeather weather) {
       _currentWeather = weather;
       notifyListeners();
     }
   }
   ```

2. **Service Classes**: Singleton-like services for API communication
   ```dart
   class ApiService {
     static const String baseUrl = 'http://localhost:8000/api/v1';
   }
   ```

3. **Custom Exceptions**: ApiException for error handling
   ```dart
   throw ApiException('Failed to fetch weather: ${response.body}');
   ```

4. **JSON Serialization**: fromJson/toJson factory methods on models
   ```dart
   factory CurrentWeather.fromJson(Map<String, dynamic> json) { ... }
   ```

### Testing Conventions

1. **Test Classes**: Group related tests in classes
   ```python
   class TestNotificationService:
       def test_service_initialization(self): ...
   ```

2. **Async Tests**: Mark with `@pytest.mark.asyncio`
   ```python
   @pytest.mark.asyncio
   async def test_send_notification(self): ...
   ```

3. **Descriptive Names**: `test_<what>_<condition>_<expected>`
   ```python
   def test_unregister_nonexistent_device(self):
   ```

4. **Fixtures**: Defined in `conftest.py` for shared setup

## Key Files to Know

| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI app initialization, CORS config |
| `backend/app/api/routes.py` | All API endpoint definitions |
| `backend/app/agent/weather_agent.py` | Letta agent config & system prompt |
| `backend/app/tools/weather.py` | Open-Meteo API integration |
| `backend/app/config.py` | Environment variable settings |
| `mobile/lib/services/api_service.dart` | Backend API client |
| `mobile/lib/providers/weather_provider.dart` | Weather state management |
| `mobile/pubspec.yaml` | Flutter dependencies |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `OPENAI_API_KEY` | Yes* | For Letta agent (if using OpenAI) |
| `DEBUG` | No | Enable debug mode (default: false) |
| `API_HOST` | No | API host (default: 0.0.0.0) |
| `API_PORT` | No | API port (default: 8000) |
| `GOOGLE_CLIENT_ID` | No | Google Calendar OAuth |
| `GOOGLE_CLIENT_SECRET` | No | Google Calendar OAuth |

*Required for full Letta agent functionality

## Important Considerations

### When Modifying Backend Code

1. **Always run tests** after changes: `pytest`
2. **Check type hints** match Pydantic schemas
3. **Update docstrings** when changing function signatures
4. **CORS is wide open** (`allow_origins=["*"]`) - consider for production
5. **Tools are modular** - each in separate file, easy to add new ones

### When Modifying Mobile Code

1. **Update baseUrl** in `api_service.dart` for physical devices
2. **Provider changes** require widget rebuild consideration
3. **Check pubspec.yaml** versions when adding dependencies
4. **Firebase setup** required for push notifications

### External API Behavior

1. **Open-Meteo**: Free, no auth, 16-day max forecast
2. **Nominatim**: Free, rate limited, requires User-Agent
3. **Google Calendar**: OAuth 2.0 required, needs `credentials.json`
4. **Firebase**: Service account needed for production

## Common Tasks

### Adding a New API Endpoint

1. Define Pydantic models in `backend/app/models/schemas.py`
2. Add route function in `backend/app/api/routes.py`
3. Write tests in `backend/tests/`
4. Update mobile `api_service.dart` if needed

### Adding a New Tool for the Agent

1. Create file in `backend/app/tools/`
2. Export in `backend/app/tools/__init__.py`
3. Register in `backend/app/agent/weather_agent.py`
4. Add tests in `backend/tests/`

### Adding a New Mobile Screen

1. Create screen in `mobile/lib/screens/`
2. Add provider if state needed in `mobile/lib/providers/`
3. Update navigation in `main.dart` or parent screens
4. Create widgets in `mobile/lib/widgets/` if reusable

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Backend won't start | Check Python 3.11+, run `pip install -r requirements.txt` |
| Mobile can't connect | Update `baseUrl` in `api_service.dart`, use machine IP not localhost |
| Tests fail with async errors | Ensure `pytest-asyncio` installed, check `conftest.py` fixtures |
| Calendar not working | Complete OAuth flow, ensure `credentials.json` exists |
| Weather data empty | Check coordinates are valid (-90 to 90 lat, -180 to 180 lon) |

## Architecture Notes

- **Backend uses singleton pattern** for services (get_notification_service, etc.)
- **Agent manager** handles user-to-agent mapping with in-memory storage
- **Mobile uses Provider** for reactive UI updates
- **All weather tools return standardized dict structures**
- **WMO weather codes** mapped to descriptions in `weather.py`
