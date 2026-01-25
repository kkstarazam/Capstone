"""Letta-based Weather Intelligence Agent.

This module configures and manages the stateful weather assistant
using Letta's memory and tool capabilities.
"""
from typing import Optional, List
import logging

# Try to import from new letta_client API
try:
    from letta_client import Letta
    from letta import LLMConfig, EmbeddingConfig
    LETTA_AVAILABLE = True
except ImportError:
    LETTA_AVAILABLE = False
    Letta = None
    LLMConfig = None
    EmbeddingConfig = None

from ..tools import weather, geocoding, calendar

logger = logging.getLogger(__name__)


# Weather Assistant System Prompt
WEATHER_AGENT_PERSONA = """You are a friendly and helpful Weather Intelligence Assistant. Your purpose is to help users with weather-related queries and planning.

Your capabilities:
1. Provide current weather conditions for any location
2. Give detailed weather forecasts (hourly and daily)
3. Help plan activities based on weather conditions
4. Check calendar events and suggest weather-appropriate times
5. Remember user preferences (temperature units, favorite locations, activities)
6. Proactively alert users about weather changes affecting their plans

Personality traits:
- Friendly and conversational, but concise
- Proactive in offering helpful suggestions
- Remember past conversations and user preferences
- Use weather emojis sparingly to enhance communication
- Always explain weather in practical terms (what to wear, what activities are suitable)

When responding:
- Start with the most relevant information first
- Provide specific temperatures and conditions
- Offer actionable recommendations
- Reference the user's schedule when relevant
- Remember and use the user's preferred temperature unit

Important: Always use the available tools to get real, accurate weather data. Never make up weather information."""


WEATHER_AGENT_HUMAN = """About the user:
- Name: Not yet known (ask if needed for personalization)
- Preferred temperature unit: Fahrenheit (update when user specifies)
- Home location: Not yet set
- Favorite locations: None saved yet
- Regular activities: None tracked yet

Recent context:
- Last checked location: None
- Weather alerts acknowledged: None"""


def get_weather_tools() -> List[dict]:
    """
    Define the tools available to the weather agent.

    Returns:
        List of tool definitions for Letta.
    """
    tools = [
        {
            "name": "get_current_weather",
            "description": "Get current weather conditions for a specific location. Use this when the user asks about current weather, temperature, or conditions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the location"
                    },
                    "temperature_unit": {
                        "type": "string",
                        "enum": ["fahrenheit", "celsius"],
                        "description": "Temperature unit preference",
                        "default": "fahrenheit"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        },
        {
            "name": "get_weather_forecast",
            "description": "Get weather forecast for upcoming days. Use this when the user asks about future weather or wants to plan activities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the location"
                    },
                    "days": {
                        "type": "integer",
                        "description": "Number of days to forecast (1-16)",
                        "default": 7
                    },
                    "temperature_unit": {
                        "type": "string",
                        "enum": ["fahrenheit", "celsius"],
                        "description": "Temperature unit preference",
                        "default": "fahrenheit"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        },
        {
            "name": "get_hourly_forecast",
            "description": "Get detailed hourly weather forecast. Use this for precise timing of activities or when user needs hour-by-hour weather info.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude of the location"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude of the location"
                    },
                    "hours": {
                        "type": "integer",
                        "description": "Number of hours to forecast (max 384)",
                        "default": 24
                    },
                    "temperature_unit": {
                        "type": "string",
                        "enum": ["fahrenheit", "celsius"],
                        "description": "Temperature unit preference",
                        "default": "fahrenheit"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        },
        {
            "name": "geocode_location",
            "description": "Convert a place name or address to coordinates. Use this when the user mentions a location by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Place name, address, or city to search for"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results",
                        "default": 3
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "reverse_geocode",
            "description": "Convert coordinates to a place name/address. Use this to identify a location from coordinates.",
            "parameters": {
                "type": "object",
                "properties": {
                    "latitude": {
                        "type": "number",
                        "description": "Latitude"
                    },
                    "longitude": {
                        "type": "number",
                        "description": "Longitude"
                    }
                },
                "required": ["latitude", "longitude"]
            }
        },
        {
            "name": "get_calendar_events",
            "description": "Get the user's upcoming calendar events. Use this to check their schedule when planning weather-dependent activities.",
            "parameters": {
                "type": "object",
                "properties": {
                    "days_ahead": {
                        "type": "integer",
                        "description": "Number of days ahead to check",
                        "default": 7
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of events to return",
                        "default": 10
                    }
                },
                "required": []
            }
        },
        {
            "name": "create_weather_reminder",
            "description": "Create a weather-related reminder in the user's calendar. Use this when suggesting they bring an umbrella, jacket, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Reminder title (e.g., 'Bring umbrella')"
                    },
                    "event_time": {
                        "type": "string",
                        "description": "ISO format datetime for the reminder"
                    },
                    "weather_note": {
                        "type": "string",
                        "description": "Weather-related reason for the reminder"
                    }
                },
                "required": ["title", "event_time", "weather_note"]
            }
        }
    ]

    return tools


class WeatherAgentManager:
    """Manager for creating and interacting with Weather Intelligence Agents."""

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize the Weather Agent Manager.

        Args:
            base_url: Optional Letta server URL (uses default if not provided)
        """
        self.base_url = base_url or "http://localhost:8283"
        self._agents = {}
        self._client = None
        self._letta_available = False

        # Try to initialize Letta client
        if LETTA_AVAILABLE:
            try:
                self._client = Letta(base_url=self.base_url)
                # Test connection
                self._client.health.check()
                self._letta_available = True
                logger.info("Letta client connected successfully")
            except Exception as e:
                logger.warning(f"Letta server not available: {e}. Running in standalone mode.")
                self._letta_available = False
        else:
            logger.warning("Letta client not installed. Running in standalone mode.")

    @property
    def client(self):
        """Get the Letta client if available."""
        return self._client

    def create_agent(self, user_id: str) -> str:
        """
        Create a new weather agent for a user.

        Args:
            user_id: Unique identifier for the user

        Returns:
            Agent ID for the created agent.
        """
        # If Letta is not available, use a simple local agent ID
        if not self._letta_available:
            agent_id = f"local_agent_{user_id}"
            self._agents[user_id] = agent_id
            return agent_id

        try:
            # Check if agent already exists for this user
            existing_agents = self._client.agents.list()
            for agent in existing_agents:
                if agent.name == f"weather_agent_{user_id}":
                    self._agents[user_id] = agent.id
                    return agent.id

            # Create the agent with new API
            agent_state = self._client.agents.create(
                name=f"weather_agent_{user_id}",
                system=WEATHER_AGENT_PERSONA,
                memory_blocks=[
                    {"label": "human", "value": WEATHER_AGENT_HUMAN},
                    {"label": "persona", "value": WEATHER_AGENT_PERSONA}
                ],
                model="gpt-4o-mini",
                embedding="text-embedding-ada-002"
            )

            # Register tools with the agent
            self._register_tools(agent_state.id)

            self._agents[user_id] = agent_state.id
            return agent_state.id
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            # Fallback to local agent
            agent_id = f"local_agent_{user_id}"
            self._agents[user_id] = agent_id
            return agent_id

    def _register_tools(self, agent_id: str):
        """Register weather tools with an agent."""
        if not self._letta_available:
            return

        tools = get_weather_tools()
        for tool_def in tools:
            try:
                # Get source code for the tool function
                func = self._get_tool_function(tool_def["name"])
                if func is None:
                    continue

                import inspect
                source_code = inspect.getsource(func)

                tool = self._client.tools.create(
                    source_code=source_code,
                    description=tool_def.get("description", ""),
                    tags=["weather", "utility"]
                )
                # Add tool to agent
                self._client.agents.tools.create(agent_id=agent_id, tool_id=tool.id)
            except Exception as e:
                logger.warning(f"Could not register tool {tool_def['name']}: {e}")

    def _get_tool_function(self, name: str):
        """Get the actual function for a tool name."""
        tool_functions = {
            "get_current_weather": weather.get_current_weather,
            "get_weather_forecast": weather.get_weather_forecast,
            "get_hourly_forecast": weather.get_hourly_forecast,
            "geocode_location": geocoding.geocode_location,
            "reverse_geocode": geocoding.reverse_geocode,
            "get_calendar_events": calendar.get_calendar_events,
            "create_weather_reminder": calendar.create_weather_reminder,
        }
        return tool_functions.get(name)

    def get_agent_id(self, user_id: str) -> Optional[str]:
        """
        Get the agent ID for a user.

        Args:
            user_id: User identifier

        Returns:
            Agent ID if exists, None otherwise.
        """
        if user_id in self._agents:
            return self._agents[user_id]

        if not self._letta_available:
            return None

        try:
            # Check if agent exists in Letta
            existing_agents = self._client.agents.list()
            for agent in existing_agents:
                if agent.name == f"weather_agent_{user_id}":
                    self._agents[user_id] = agent.id
                    return agent.id
        except Exception as e:
            logger.warning(f"Error listing agents: {e}")

        return None

    async def send_message(self, user_id: str, message: str) -> dict:
        """
        Send a message to the user's weather agent.

        Args:
            user_id: User identifier
            message: User's message

        Returns:
            Agent's response.
        """
        agent_id = self.get_agent_id(user_id)
        if not agent_id:
            agent_id = self.create_agent(user_id)

        # If Letta is not available, provide a fallback response
        if not self._letta_available or agent_id.startswith("local_agent_"):
            return await self._handle_message_locally(user_id, message)

        try:
            response = self._client.agents.messages.create(
                agent_id=agent_id,
                input=message
            )

            # Extract the assistant's response
            assistant_messages = []
            tool_calls = []

            for msg in response.messages:
                if hasattr(msg, 'assistant_message') and msg.assistant_message:
                    assistant_messages.append(msg.assistant_message)
                if hasattr(msg, 'tool_call') and msg.tool_call:
                    tool_calls.append({
                        "name": msg.tool_call.name,
                        "arguments": msg.tool_call.arguments
                    })

            return {
                "response": " ".join(assistant_messages) if assistant_messages else "I processed your request.",
                "tool_calls": tool_calls,
                "agent_id": agent_id
            }
        except Exception as e:
            logger.error(f"Error sending message to Letta: {e}")
            return await self._handle_message_locally(user_id, message)

    async def _handle_message_locally(self, user_id: str, message: str) -> dict:
        """
        Handle messages locally when Letta is not available.

        Provides basic weather functionality without AI agent.
        """
        message_lower = message.lower()

        # Simple keyword-based response
        if "weather" in message_lower or "temperature" in message_lower:
            return {
                "response": "I can help with weather information! Please use the weather endpoints directly (/api/v1/weather/current or /api/v1/weather/forecast) with your location coordinates, or search for a location using /api/v1/geocode.",
                "tool_calls": [],
                "agent_id": f"local_agent_{user_id}"
            }
        elif "forecast" in message_lower:
            return {
                "response": "For weather forecasts, please use the /api/v1/weather/forecast endpoint with latitude and longitude coordinates.",
                "tool_calls": [],
                "agent_id": f"local_agent_{user_id}"
            }
        else:
            return {
                "response": "I'm the Weather Intelligence Assistant. I can help you with weather information, forecasts, and location searches. The full AI capabilities require a Letta server connection. For now, please use the direct API endpoints for weather data.",
                "tool_calls": [],
                "agent_id": f"local_agent_{user_id}"
            }

    def update_user_preferences(self, user_id: str, preferences: dict):
        """
        Update user preferences in the agent's memory.

        Args:
            user_id: User identifier
            preferences: Dictionary of preferences to update
        """
        agent_id = self.get_agent_id(user_id)
        if not agent_id or not self._letta_available:
            return

        try:
            # Update preferences via agent blocks
            updates = []
            if "temperature_unit" in preferences:
                updates.append(f"Preferred temperature unit: {preferences['temperature_unit']}")
            if "home_location" in preferences:
                updates.append(f"Home location: {preferences['home_location']}")
            if "name" in preferences:
                updates.append(f"Name: {preferences['name']}")

            if updates:
                # Update the human block with new preferences
                human_block = WEATHER_AGENT_HUMAN + "\n\nUpdated preferences:\n" + "\n".join(updates)
                self._client.agents.blocks.update(
                    agent_id=agent_id,
                    block_label="human",
                    value=human_block
                )
        except Exception as e:
            logger.warning(f"Error updating preferences: {e}")

    def delete_agent(self, user_id: str):
        """
        Delete a user's weather agent.

        Args:
            user_id: User identifier
        """
        agent_id = self.get_agent_id(user_id)
        if agent_id:
            if self._letta_available and not agent_id.startswith("local_agent_"):
                try:
                    self._client.agents.delete(agent_id)
                except Exception as e:
                    logger.warning(f"Error deleting agent from Letta: {e}")
            if user_id in self._agents:
                del self._agents[user_id]


# Global agent manager instance
agent_manager: Optional[WeatherAgentManager] = None


def get_agent_manager() -> WeatherAgentManager:
    """Get or create the global agent manager."""
    global agent_manager
    if agent_manager is None:
        agent_manager = WeatherAgentManager()
    return agent_manager
