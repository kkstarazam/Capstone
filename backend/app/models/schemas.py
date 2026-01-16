"""Pydantic models for API request/response schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============== Chat Models ==============

class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    """Request to send a message to the weather agent."""
    user_id: str = Field(..., description="Unique user identifier")
    message: str = Field(..., description="User's message")


class ChatResponse(BaseModel):
    """Response from the weather agent."""
    response: str = Field(..., description="Agent's response message")
    tool_calls: Optional[List[dict]] = Field(default=None, description="Tools called during processing")
    agent_id: str = Field(..., description="Agent ID that handled the request")


# ============== Weather Models ==============

class LocationRequest(BaseModel):
    """Request with location information."""
    latitude: float = Field(..., description="Latitude")
    longitude: float = Field(..., description="Longitude")


class GeocodeRequest(BaseModel):
    """Request to geocode a location."""
    query: str = Field(..., description="Place name or address to search")
    limit: int = Field(default=5, description="Maximum results")


class CurrentWeatherResponse(BaseModel):
    """Current weather conditions."""
    temperature: float
    feels_like: float
    humidity: int
    precipitation: float
    cloud_cover: int
    wind_speed: float
    wind_direction: int
    weather_description: str
    is_day: bool
    temperature_unit: str


class DailyForecast(BaseModel):
    """Single day weather forecast."""
    date: str
    weather_description: str
    temp_high: float
    temp_low: float
    precipitation_probability: Optional[int]
    precipitation: Optional[float]
    wind_speed_max: Optional[float]
    uv_index_max: Optional[float]


class ForecastResponse(BaseModel):
    """Weather forecast response."""
    forecasts: List[DailyForecast]
    temperature_unit: str
    timezone: str


# ============== User Preferences ==============

class UserPreferences(BaseModel):
    """User preference settings."""
    temperature_unit: str = Field(default="fahrenheit", description="fahrenheit or celsius")
    home_location: Optional[dict] = Field(default=None, description="Home location coordinates and name")
    favorite_locations: List[dict] = Field(default_factory=list, description="Saved favorite locations")
    notification_enabled: bool = Field(default=True, description="Enable push notifications")


class UpdatePreferencesRequest(BaseModel):
    """Request to update user preferences."""
    user_id: str = Field(..., description="User identifier")
    preferences: UserPreferences


# ============== Calendar Models ==============

class CalendarEvent(BaseModel):
    """A calendar event."""
    id: str
    summary: str
    description: Optional[str]
    location: Optional[str]
    start: str
    end: str
    all_day: bool


class CreateReminderRequest(BaseModel):
    """Request to create a weather reminder."""
    user_id: str
    title: str
    event_time: datetime
    weather_note: str


# ============== Agent Management ==============

class CreateAgentRequest(BaseModel):
    """Request to create a new weather agent."""
    user_id: str = Field(..., description="Unique user identifier")


class AgentResponse(BaseModel):
    """Response with agent information."""
    agent_id: str
    user_id: str
    status: str = "active"
