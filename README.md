# Capstone
# Weather Intelligence Agent 🌤️

An AI-powered mobile weather assistant that provides personalized weather insights, smart recommendations, and proactive alerts based on your schedule and preferences.

## Overview

This mobile application combines weather intelligence with calendar awareness to help you plan your day.  The AI agent doesn't just tell you the weather—it understands your schedule, remembers your preferences, and proactively helps you make better decisions.

## Features

### 🤖 Intelligent Conversations
- Natural language weather queries
- Context-aware responses based on your schedule
- Personalized recommendations for activities and clothing

### 📅 Calendar Integration
- Automatically checks weather for scheduled events
- Suggests optimal times for outdoor activities
- Sends alerts when weather might affect your plans

### 🧠 Long-term Memory
- Remembers your preferred locations
- Learns your activity patterns
- Stores temperature unit preferences (Fahrenheit/Celsius)
- Recalls your weather-sensitive commitments

### 🔔 Proactive Assistance
- Alerts for severe weather warnings
- Notifications when weather changes affect your schedule
- Smart suggestions based on forecast and your calendar

## Required Capabilities

### MCP Tools

1. **Weather API Tool**
   - Real-time weather data
   - 7-day forecasts
   - Severe weather alerts
   - Historical weather data

2. **Location/Geocoding Tool**
   - Convert addresses to coordinates
   - Detect current location
   - Save multiple favorite locations
   - Support for international locations

3. **Calendar/Scheduling Tool**
   - Read calendar events
   - Create weather-based reminders
   - Suggest reschedules for weather-sensitive events
   - Add preparation reminders (e.g., "bring umbrella")

### Memory System

The agent maintains long-term memory for:
- **User Preferences**: Temperature units, notification settings, favorite locations
- **Activity Patterns**: Regular outdoor activities, commute times, typical schedules
- **Historical Interactions**: Past queries, favorite weather-dependent activities
- **Location History**: Frequently checked locations and travel patterns

## Use Case Examples

### Morning Briefing
```
User: "What's my day looking like?"

Agent:  "Good morning! It's currently 52°F and cloudy. 
You have a lunch meeting at noon—perfect timing as 
it'll be 65°F and sunny by then. However, your 5pm 
soccer practice might see light rain. I recommend 
bringing a jacket."
```

### Activity Planning
```
User: "When should I go for a run this week?"

Agent: "Based on your usual running times and this week's 
forecast, I recommend: 
- Wednesday 6am:  58°F, clear skies
- Friday 6am: 62°F, partly cloudy
- Saturday 8am: 68°F, sunny (best option!)

Would you like me to add these to your calendar?"
```

### Proactive Alerts
```
Agent: "⚠️ Weather Update: Thunderstorms expected at 
3pm today. I noticed you have 'Park Meetup' scheduled 
at 3: 30pm.  Would you like suggestions for indoor 
alternatives?"
```

### Travel Planning
```
User: "I'm traveling to Boston next week"

Agent: "I'll track Boston's weather for you. Next week 
looks cold—highs around 35°F with possible snow on 
Tuesday. I've added this to your tracked locations. 
Want packing suggestions?"
```

## Technical Architecture

### Mobile UI
- Cross-platform mobile application
- Chat-based interface for natural conversations
- Visual weather displays and forecasts
- Push notification support

### LLM Agent
- **Google Gemini 1.5 Flash**
- Free tier with generous rate limits (1500 requests per day)
- Fast response times ideal for real-time mobile chat
- Native function calling for seamless MCP tool integration
- Multimodal capabilities (can process text and images)
- Accessed via Google AI Studio API

### MCP Tools Implementation
1. **Weather API: OpenWeatherMap**
   - Free tier: 1,000 API calls/day
   - Provides current weather, 5-day forecasts, and severe weather alerts
   - Global coverage with 200,000+ cities
   - API Documentation: https://openweathermap.org/api
   - Endpoints used:
     - Current Weather Data
     - 5 Day / 3 Hour Forecast
     - Weather Alerts

2. **Location/Geocoding: OpenWeatherMap Geocoding API**
   - Included free with OpenWeatherMap API key
   - Converts city names, ZIP codes, and addresses to geographic coordinates
   - Reverse geocoding (coordinates to location names)
   - Supports international locations
   - API Documentation: https://openweathermap.org/api/geocoding-api

3. **Calendar Integration: Google Calendar API**
   - Free tier with generous quotas
   - Full read/write access to user calendars
   - Event creation, modification, and deletion
   - Recurring event support
   - Push notifications for calendar changes
   - API Documentation: https://developers.google.com/calendar/api
   - Integrates seamlessly with Google account ecosystem

### Memory Storage
- _(To be determined)_

### Additional Technologies
- _(To be determined)_

## Installation

_(To be added during implementation)_

## Usage

_(To be added during implementation)_

## Development

_(To be added during implementation)_

## Future Enhancements

- Integration with smart home devices
- Photo recognition for weather condition verification
- Community weather reports and updates
- Travel itinerary weather tracking
- Health recommendations based on weather (air quality, UV index)
- Multi-user support for family or group planning

## License

_(To be determined)_

## Contributors

- kkstarazam

## Acknowledgments

Built as part of an agentic application course project.

---

**Note**: This README describes the planned application.  Implementation details will be added as development progresses. 
