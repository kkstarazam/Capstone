"""FastAPI routes for the Weather Intelligence Agent API."""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from datetime import datetime, timedelta

from ..models.schemas import (
    ChatRequest,
    ChatResponse,
    LocationRequest,
    GeocodeRequest,
    CurrentWeatherResponse,
    ForecastResponse,
    UserPreferences,
    UpdatePreferencesRequest,
    CreateAgentRequest,
    AgentResponse,
    CreateReminderRequest,
)
from ..tools import weather, geocoding, calendar
from ..agent.weather_agent import get_agent_manager, WeatherAgentManager
from ..services.notifications import get_notification_service
from ..services.weather_alerts import get_weather_alert_service


router = APIRouter()


# ============== Chat Endpoints ==============

@router.post("/chat", response_model=ChatResponse, tags=["Chat"])
async def send_message(request: ChatRequest):
    """
    Send a message to the weather agent and get a response.

    The agent will process the message, potentially calling weather,
    location, or calendar tools, and return a contextual response.
    """
    try:
        manager = get_agent_manager()
        result = await manager.send_message(request.user_id, request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")


# ============== Weather Endpoints ==============

@router.post("/weather/current", tags=["Weather"])
async def get_current_weather(request: LocationRequest, temperature_unit: str = "fahrenheit"):
    """Get current weather for a location."""
    try:
        result = await weather.get_current_weather(
            latitude=request.latitude,
            longitude=request.longitude,
            temperature_unit=temperature_unit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching weather: {str(e)}")


@router.post("/weather/forecast", tags=["Weather"])
async def get_forecast(
    request: LocationRequest,
    days: int = 7,
    temperature_unit: str = "fahrenheit"
):
    """Get weather forecast for a location."""
    try:
        result = await weather.get_weather_forecast(
            latitude=request.latitude,
            longitude=request.longitude,
            days=days,
            temperature_unit=temperature_unit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching forecast: {str(e)}")


@router.post("/weather/hourly", tags=["Weather"])
async def get_hourly(
    request: LocationRequest,
    hours: int = 24,
    temperature_unit: str = "fahrenheit"
):
    """Get hourly weather forecast for a location."""
    try:
        result = await weather.get_hourly_forecast(
            latitude=request.latitude,
            longitude=request.longitude,
            hours=hours,
            temperature_unit=temperature_unit
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hourly forecast: {str(e)}")


# ============== Geocoding Endpoints ==============

@router.post("/geocode", tags=["Location"])
async def geocode(request: GeocodeRequest):
    """Convert a place name or address to coordinates."""
    try:
        results = await geocoding.geocode_location(
            query=request.query,
            limit=request.limit
        )
        return {"locations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error geocoding: {str(e)}")


@router.post("/reverse-geocode", tags=["Location"])
async def reverse_geocode(request: LocationRequest):
    """Convert coordinates to a place name/address."""
    try:
        result = await geocoding.reverse_geocode(
            latitude=request.latitude,
            longitude=request.longitude
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reverse geocoding: {str(e)}")


# ============== Calendar Endpoints ==============

@router.get("/calendar/events", tags=["Calendar"])
async def get_events(days_ahead: int = 7, max_results: int = 10):
    """Get upcoming calendar events."""
    try:
        # Check if calendar is available
        available = await calendar.check_calendar_availability()
        if not available:
            raise HTTPException(
                status_code=503,
                detail="Google Calendar not configured. Please set up OAuth credentials."
            )

        events = await calendar.get_calendar_events(
            start_date=datetime.utcnow(),
            end_date=datetime.utcnow() + timedelta(days=days_ahead),
            max_results=max_results
        )
        return {"events": events}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching events: {str(e)}")


@router.post("/calendar/reminder", tags=["Calendar"])
async def create_reminder(request: CreateReminderRequest):
    """Create a weather-related reminder."""
    try:
        available = await calendar.check_calendar_availability()
        if not available:
            raise HTTPException(
                status_code=503,
                detail="Google Calendar not configured."
            )

        result = await calendar.create_weather_reminder(
            title=request.title,
            event_time=request.event_time,
            weather_note=request.weather_note
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating reminder: {str(e)}")


# ============== Agent Management Endpoints ==============

@router.post("/agent/create", response_model=AgentResponse, tags=["Agent"])
async def create_agent(request: CreateAgentRequest):
    """Create a new weather agent for a user."""
    try:
        manager = get_agent_manager()
        agent_id = manager.create_agent(request.user_id)
        return AgentResponse(agent_id=agent_id, user_id=request.user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating agent: {str(e)}")


@router.get("/agent/{user_id}", response_model=AgentResponse, tags=["Agent"])
async def get_agent(user_id: str):
    """Get agent info for a user."""
    try:
        manager = get_agent_manager()
        agent_id = manager.get_agent_id(user_id)
        if not agent_id:
            raise HTTPException(status_code=404, detail="Agent not found")
        return AgentResponse(agent_id=agent_id, user_id=user_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching agent: {str(e)}")


@router.delete("/agent/{user_id}", tags=["Agent"])
async def delete_agent(user_id: str):
    """Delete a user's weather agent."""
    try:
        manager = get_agent_manager()
        manager.delete_agent(user_id)
        return {"status": "deleted", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting agent: {str(e)}")


@router.put("/agent/{user_id}/preferences", tags=["Agent"])
async def update_preferences(user_id: str, preferences: UserPreferences):
    """Update user preferences in the agent's memory."""
    try:
        manager = get_agent_manager()
        manager.update_user_preferences(user_id, preferences.model_dump())
        return {"status": "updated", "user_id": user_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")


# ============== Health Check ==============

@router.get("/health", tags=["System"])
async def health_check():
    """Check API health status."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "weather_api": "available",
            "geocoding": "available",
            "calendar": await calendar.check_calendar_availability(),
            "notifications": get_notification_service().is_available
        }
    }


# ============== Notification Endpoints ==============

@router.post("/notifications/register", tags=["Notifications"])
async def register_device(user_id: str, device_token: str):
    """Register a device for push notifications."""
    service = get_notification_service()
    success = service.register_device(user_id, device_token)
    return {"status": "registered" if success else "failed", "user_id": user_id}


@router.delete("/notifications/unregister/{user_id}", tags=["Notifications"])
async def unregister_device(user_id: str):
    """Unregister a device from push notifications."""
    service = get_notification_service()
    success = service.unregister_device(user_id)
    return {"status": "unregistered" if success else "not_found", "user_id": user_id}


@router.post("/notifications/test", tags=["Notifications"])
async def send_test_notification(user_id: str, title: str, body: str):
    """Send a test notification to a user."""
    service = get_notification_service()
    success = await service.send_notification(user_id, title, body)
    return {"status": "sent" if success else "failed", "user_id": user_id}


# ============== Weather Alert Subscription Endpoints ==============

@router.post("/alerts/subscribe", tags=["Alerts"])
async def subscribe_to_alerts(
    user_id: str,
    latitude: float,
    longitude: float,
    location_name: str,
    rain_alerts: bool = True,
    temperature_alerts: bool = True,
    severe_weather_alerts: bool = True,
):
    """Subscribe to weather alerts for a location."""
    service = get_weather_alert_service()
    success = service.subscribe(
        user_id=user_id,
        latitude=latitude,
        longitude=longitude,
        location_name=location_name,
        rain_alerts=rain_alerts,
        temperature_alerts=temperature_alerts,
        severe_weather_alerts=severe_weather_alerts,
    )
    return {"status": "subscribed" if success else "failed", "user_id": user_id}


@router.delete("/alerts/unsubscribe/{user_id}", tags=["Alerts"])
async def unsubscribe_from_alerts(user_id: str):
    """Unsubscribe from weather alerts."""
    service = get_weather_alert_service()
    success = service.unsubscribe(user_id)
    return {"status": "unsubscribed" if success else "not_found", "user_id": user_id}


@router.post("/alerts/check/{user_id}", tags=["Alerts"])
async def check_alerts_now(user_id: str):
    """Manually trigger an alert check for a user."""
    service = get_weather_alert_service()
    alerts = await service.check_weather_for_user(user_id)
    return {"user_id": user_id, "alerts": alerts, "count": len(alerts)}
