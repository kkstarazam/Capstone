"""Weather alert service for proactive notifications.

This service monitors weather conditions and sends alerts
when significant changes or severe weather is detected.
"""
import asyncio
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from dataclasses import dataclass

from ..tools import weather, geocoding
from .notifications import get_notification_service


@dataclass
class UserWeatherSubscription:
    """User's weather monitoring subscription."""
    user_id: str
    latitude: float
    longitude: float
    location_name: str
    alerts_enabled: bool = True
    rain_alerts: bool = True
    temperature_alerts: bool = True
    severe_weather_alerts: bool = True
    temperature_threshold_high: float = 95.0  # Fahrenheit
    temperature_threshold_low: float = 32.0   # Fahrenheit
    last_checked: Optional[datetime] = None
    last_conditions: Optional[Dict[str, Any]] = None


class WeatherAlertService:
    """Service for monitoring weather and sending proactive alerts."""

    def __init__(self):
        """Initialize the weather alert service."""
        self._subscriptions: Dict[str, UserWeatherSubscription] = {}
        self._running = False
        self._check_interval = 1800  # 30 minutes

    def subscribe(
        self,
        user_id: str,
        latitude: float,
        longitude: float,
        location_name: str,
        **kwargs,
    ) -> bool:
        """
        Subscribe a user to weather alerts for a location.

        Args:
            user_id: User identifier
            latitude: Location latitude
            longitude: Location longitude
            location_name: Human-readable location name
            **kwargs: Optional subscription settings

        Returns:
            True if subscription successful.
        """
        self._subscriptions[user_id] = UserWeatherSubscription(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            location_name=location_name,
            **kwargs,
        )
        return True

    def unsubscribe(self, user_id: str) -> bool:
        """
        Unsubscribe a user from weather alerts.

        Args:
            user_id: User identifier

        Returns:
            True if unsubscription successful.
        """
        if user_id in self._subscriptions:
            del self._subscriptions[user_id]
            return True
        return False

    def update_subscription(self, user_id: str, **kwargs) -> bool:
        """
        Update a user's subscription settings.

        Args:
            user_id: User identifier
            **kwargs: Settings to update

        Returns:
            True if update successful.
        """
        if user_id not in self._subscriptions:
            return False

        sub = self._subscriptions[user_id]
        for key, value in kwargs.items():
            if hasattr(sub, key):
                setattr(sub, key, value)
        return True

    async def check_weather_for_user(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Check weather conditions for a user and generate alerts.

        Args:
            user_id: User identifier

        Returns:
            List of generated alerts.
        """
        if user_id not in self._subscriptions:
            return []

        sub = self._subscriptions[user_id]
        if not sub.alerts_enabled:
            return []

        alerts = []
        notification_service = get_notification_service()

        try:
            # Get current weather
            current = await weather.get_current_weather(
                latitude=sub.latitude,
                longitude=sub.longitude,
            )

            # Get forecast for rain prediction
            forecast = await weather.get_hourly_forecast(
                latitude=sub.latitude,
                longitude=sub.longitude,
                hours=24,
            )

            # Check for severe weather
            if sub.severe_weather_alerts:
                severe_alert = self._check_severe_weather(current, sub)
                if severe_alert:
                    alerts.append(severe_alert)
                    await notification_service.send_weather_alert(
                        user_id=user_id,
                        alert_type=severe_alert["type"],
                        location=sub.location_name,
                        message=severe_alert["message"],
                        severity="severe",
                    )

            # Check for rain
            if sub.rain_alerts:
                rain_alert = self._check_rain(current, forecast, sub)
                if rain_alert:
                    alerts.append(rain_alert)
                    await notification_service.send_weather_alert(
                        user_id=user_id,
                        alert_type="rain",
                        location=sub.location_name,
                        message=rain_alert["message"],
                        severity="warning",
                    )

            # Check temperature extremes
            if sub.temperature_alerts:
                temp_alert = self._check_temperature(current, sub)
                if temp_alert:
                    alerts.append(temp_alert)
                    await notification_service.send_weather_alert(
                        user_id=user_id,
                        alert_type="temperature",
                        location=sub.location_name,
                        message=temp_alert["message"],
                        severity="info",
                    )

            # Update last checked
            sub.last_checked = datetime.utcnow()
            sub.last_conditions = current

        except Exception as e:
            print(f"Error checking weather for user {user_id}: {e}")

        return alerts

    def _check_severe_weather(
        self,
        current: Dict[str, Any],
        sub: UserWeatherSubscription,
    ) -> Optional[Dict[str, Any]]:
        """Check for severe weather conditions."""
        weather_code = current.get("weather_code", 0)
        description = current.get("weather_description", "")

        # Severe weather codes (thunderstorms, heavy precipitation)
        severe_codes = [95, 96, 99, 65, 67, 75, 82, 86]

        if weather_code in severe_codes:
            return {
                "type": "severe_weather",
                "message": f"Severe weather alert: {description}. Take precautions!",
                "weather_code": weather_code,
            }

        # Check for high winds
        wind_speed = current.get("wind_speed", 0)
        wind_gusts = current.get("wind_gusts", 0)
        if wind_gusts > 50 or wind_speed > 35:
            return {
                "type": "high_wind",
                "message": f"High wind warning: Gusts up to {wind_gusts:.0f} mph",
                "wind_speed": wind_speed,
                "wind_gusts": wind_gusts,
            }

        return None

    def _check_rain(
        self,
        current: Dict[str, Any],
        forecast: Dict[str, Any],
        sub: UserWeatherSubscription,
    ) -> Optional[Dict[str, Any]]:
        """Check for upcoming rain."""
        # Skip if already raining
        if current.get("precipitation", 0) > 0:
            return None

        # Check if rain is coming in the next few hours
        forecasts = forecast.get("forecasts", [])
        for i, hour_forecast in enumerate(forecasts[:6]):  # Next 6 hours
            precip_prob = hour_forecast.get("precipitation_probability", 0)
            if precip_prob and precip_prob > 60:
                time_str = hour_forecast.get("time", "")
                return {
                    "type": "rain_coming",
                    "message": f"Rain expected in ~{i+1} hour(s) ({precip_prob}% chance). Consider bringing an umbrella!",
                    "probability": precip_prob,
                    "time": time_str,
                }

        return None

    def _check_temperature(
        self,
        current: Dict[str, Any],
        sub: UserWeatherSubscription,
    ) -> Optional[Dict[str, Any]]:
        """Check for temperature extremes."""
        temp = current.get("temperature", 70)

        # Only alert if conditions changed from last check
        if sub.last_conditions:
            last_temp = sub.last_conditions.get("temperature", temp)
            # Don't re-alert if temperature hasn't changed significantly
            if abs(temp - last_temp) < 5:
                return None

        if temp >= sub.temperature_threshold_high:
            return {
                "type": "high_temperature",
                "message": f"High temperature alert: {temp:.0f}°F. Stay hydrated and limit outdoor activity!",
                "temperature": temp,
            }

        if temp <= sub.temperature_threshold_low:
            return {
                "type": "low_temperature",
                "message": f"Low temperature alert: {temp:.0f}°F. Bundle up and watch for ice!",
                "temperature": temp,
            }

        return None

    async def start_monitoring(self):
        """Start the background weather monitoring loop."""
        if self._running:
            return

        self._running = True
        print("Weather alert monitoring started")

        while self._running:
            for user_id in list(self._subscriptions.keys()):
                try:
                    await self.check_weather_for_user(user_id)
                except Exception as e:
                    print(f"Error monitoring weather for {user_id}: {e}")

            # Wait before next check
            await asyncio.sleep(self._check_interval)

    def stop_monitoring(self):
        """Stop the background weather monitoring."""
        self._running = False
        print("Weather alert monitoring stopped")


# Global weather alert service instance
_weather_alert_service: Optional[WeatherAlertService] = None


def get_weather_alert_service() -> WeatherAlertService:
    """Get or create the global weather alert service."""
    global _weather_alert_service
    if _weather_alert_service is None:
        _weather_alert_service = WeatherAlertService()
    return _weather_alert_service
