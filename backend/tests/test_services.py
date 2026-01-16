"""Tests for backend services."""
import pytest
from datetime import datetime

from app.services.notifications import NotificationService, get_notification_service
from app.services.weather_alerts import WeatherAlertService, get_weather_alert_service


class TestNotificationService:
    """Tests for the notification service."""

    def test_service_initialization(self):
        """Test that notification service initializes correctly."""
        service = NotificationService()
        assert service is not None
        # Without Firebase credentials, should not be fully initialized
        assert not service.is_available

    def test_register_device(self):
        """Test device registration."""
        service = NotificationService()
        result = service.register_device("user123", "device_token_abc")
        assert result is True

    def test_get_device_token(self):
        """Test retrieving a device token."""
        service = NotificationService()
        service.register_device("user456", "device_token_def")
        token = service.get_device_token("user456")
        assert token == "device_token_def"

    def test_get_nonexistent_device_token(self):
        """Test retrieving token for non-registered user."""
        service = NotificationService()
        token = service.get_device_token("nonexistent_user")
        assert token is None

    def test_unregister_device(self):
        """Test device unregistration."""
        service = NotificationService()
        service.register_device("user789", "device_token_ghi")
        result = service.unregister_device("user789")
        assert result is True
        assert service.get_device_token("user789") is None

    def test_unregister_nonexistent_device(self):
        """Test unregistering non-existent device."""
        service = NotificationService()
        result = service.unregister_device("never_registered")
        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_without_token(self):
        """Test sending notification to user without device token."""
        service = NotificationService()
        result = await service.send_notification(
            "no_token_user",
            "Test Title",
            "Test Body"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_send_notification_with_token(self):
        """Test sending notification (logs in dev mode)."""
        service = NotificationService()
        service.register_device("test_user", "fake_token")
        result = await service.send_notification(
            "test_user",
            "Weather Alert",
            "Rain expected in 2 hours"
        )
        # In dev mode without Firebase, still returns True (logged)
        assert result is True

    @pytest.mark.asyncio
    async def test_send_weather_alert(self):
        """Test sending weather alert notification."""
        service = NotificationService()
        service.register_device("alert_user", "alert_token")
        result = await service.send_weather_alert(
            "alert_user",
            alert_type="rain",
            location="Seattle",
            message="Rain expected this afternoon",
            severity="warning"
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_send_schedule_reminder(self):
        """Test sending schedule reminder notification."""
        service = NotificationService()
        service.register_device("schedule_user", "schedule_token")
        result = await service.send_schedule_reminder(
            "schedule_user",
            event_name="Soccer Practice",
            weather_info="Light rain expected at 5pm",
            recommendation="Consider bringing rain gear"
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_send_to_multiple(self):
        """Test sending to multiple users."""
        service = NotificationService()
        service.register_device("multi_user_1", "token_1")
        service.register_device("multi_user_2", "token_2")
        service.register_device("multi_user_3", "token_3")

        results = await service.send_to_multiple(
            ["multi_user_1", "multi_user_2", "multi_user_3", "no_token"],
            "Broadcast",
            "Severe weather warning for the region"
        )

        assert results["multi_user_1"] is True
        assert results["multi_user_2"] is True
        assert results["multi_user_3"] is True
        assert results["no_token"] is False

    def test_global_service_singleton(self):
        """Test that get_notification_service returns singleton."""
        service1 = get_notification_service()
        service2 = get_notification_service()
        assert service1 is service2


class TestWeatherAlertService:
    """Tests for the weather alert service."""

    def test_service_initialization(self):
        """Test that weather alert service initializes correctly."""
        service = WeatherAlertService()
        assert service is not None
        assert service._running is False

    def test_subscribe(self):
        """Test subscribing to alerts."""
        service = WeatherAlertService()
        result = service.subscribe(
            user_id="sub_user",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="New York"
        )
        assert result is True
        assert "sub_user" in service._subscriptions

    def test_subscribe_with_options(self):
        """Test subscribing with custom options."""
        service = WeatherAlertService()
        result = service.subscribe(
            user_id="options_user",
            latitude=34.0522,
            longitude=-118.2437,
            location_name="Los Angeles",
            rain_alerts=False,
            temperature_alerts=True,
            severe_weather_alerts=True,
            temperature_threshold_high=100.0,
            temperature_threshold_low=40.0
        )
        assert result is True

        sub = service._subscriptions["options_user"]
        assert sub.rain_alerts is False
        assert sub.temperature_threshold_high == 100.0

    def test_unsubscribe(self):
        """Test unsubscribing from alerts."""
        service = WeatherAlertService()
        service.subscribe("unsub_user", 0, 0, "Test")
        result = service.unsubscribe("unsub_user")
        assert result is True
        assert "unsub_user" not in service._subscriptions

    def test_unsubscribe_nonexistent(self):
        """Test unsubscribing non-existent user."""
        service = WeatherAlertService()
        result = service.unsubscribe("never_subscribed")
        assert result is False

    def test_update_subscription(self):
        """Test updating subscription settings."""
        service = WeatherAlertService()
        service.subscribe("update_user", 0, 0, "Test")
        result = service.update_subscription(
            "update_user",
            rain_alerts=False,
            temperature_threshold_high=90.0
        )
        assert result is True

        sub = service._subscriptions["update_user"]
        assert sub.rain_alerts is False
        assert sub.temperature_threshold_high == 90.0

    def test_update_nonexistent_subscription(self):
        """Test updating non-existent subscription."""
        service = WeatherAlertService()
        result = service.update_subscription("nobody", rain_alerts=False)
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.skip(reason="Requires external network - see test_mocked_api.py for mocked version")
    async def test_check_weather_for_user(self):
        """Test checking weather for a subscribed user (requires network)."""
        service = WeatherAlertService()
        service.subscribe(
            user_id="check_user",
            latitude=47.6062,
            longitude=-122.3321,
            location_name="Seattle"
        )

        # Register device for notifications
        notif_service = get_notification_service()
        notif_service.register_device("check_user", "check_token")

        alerts = await service.check_weather_for_user("check_user")
        assert isinstance(alerts, list)

        # Verify last_checked was updated
        sub = service._subscriptions["check_user"]
        assert sub.last_checked is not None

    @pytest.mark.asyncio
    async def test_check_weather_disabled_alerts(self):
        """Test checking weather with alerts disabled."""
        service = WeatherAlertService()
        service.subscribe(
            user_id="disabled_user",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="NYC",
            alerts_enabled=False
        )

        alerts = await service.check_weather_for_user("disabled_user")
        assert alerts == []

    @pytest.mark.asyncio
    async def test_check_weather_nonexistent_user(self):
        """Test checking weather for non-subscribed user."""
        service = WeatherAlertService()
        alerts = await service.check_weather_for_user("nonexistent")
        assert alerts == []

    def test_global_service_singleton(self):
        """Test that get_weather_alert_service returns singleton."""
        service1 = get_weather_alert_service()
        service2 = get_weather_alert_service()
        assert service1 is service2


class TestAlertDetection:
    """Tests for weather alert detection logic."""

    def test_severe_weather_detection_thunderstorm(self):
        """Test detection of thunderstorm conditions."""
        service = WeatherAlertService()
        service.subscribe("severe_user", 0, 0, "Test")
        sub = service._subscriptions["severe_user"]

        # Simulate thunderstorm conditions
        current = {
            "weather_code": 95,
            "weather_description": "Thunderstorm",
            "wind_speed": 20,
            "wind_gusts": 35
        }

        alert = service._check_severe_weather(current, sub)
        assert alert is not None
        assert alert["type"] == "severe_weather"

    def test_severe_weather_detection_high_wind(self):
        """Test detection of high wind conditions."""
        service = WeatherAlertService()
        service.subscribe("wind_user", 0, 0, "Test")
        sub = service._subscriptions["wind_user"]

        # Simulate high wind conditions
        current = {
            "weather_code": 3,  # Overcast (not severe)
            "weather_description": "Overcast",
            "wind_speed": 40,
            "wind_gusts": 55
        }

        alert = service._check_severe_weather(current, sub)
        assert alert is not None
        assert alert["type"] == "high_wind"

    def test_no_severe_weather(self):
        """Test no alert for normal conditions."""
        service = WeatherAlertService()
        service.subscribe("normal_user", 0, 0, "Test")
        sub = service._subscriptions["normal_user"]

        # Normal conditions
        current = {
            "weather_code": 1,
            "weather_description": "Mainly clear",
            "wind_speed": 10,
            "wind_gusts": 15
        }

        alert = service._check_severe_weather(current, sub)
        assert alert is None

    def test_rain_detection(self):
        """Test detection of upcoming rain."""
        service = WeatherAlertService()
        service.subscribe("rain_user", 0, 0, "Test")
        sub = service._subscriptions["rain_user"]

        current = {"precipitation": 0}  # Not currently raining

        forecast = {
            "forecasts": [
                {"precipitation_probability": 20, "time": "2024-01-01T10:00"},
                {"precipitation_probability": 40, "time": "2024-01-01T11:00"},
                {"precipitation_probability": 80, "time": "2024-01-01T12:00"},
            ]
        }

        alert = service._check_rain(current, forecast, sub)
        assert alert is not None
        assert alert["type"] == "rain_coming"
        assert alert["probability"] == 80

    def test_no_rain_when_already_raining(self):
        """Test no rain alert when already raining."""
        service = WeatherAlertService()
        service.subscribe("raining_user", 0, 0, "Test")
        sub = service._subscriptions["raining_user"]

        current = {"precipitation": 0.5}  # Currently raining

        forecast = {
            "forecasts": [
                {"precipitation_probability": 90, "time": "2024-01-01T10:00"},
            ]
        }

        alert = service._check_rain(current, forecast, sub)
        assert alert is None

    def test_temperature_high_alert(self):
        """Test high temperature alert."""
        service = WeatherAlertService()
        service.subscribe("hot_user", 0, 0, "Test")
        sub = service._subscriptions["hot_user"]
        sub.temperature_threshold_high = 95.0

        current = {"temperature": 100}

        alert = service._check_temperature(current, sub)
        assert alert is not None
        assert alert["type"] == "high_temperature"

    def test_temperature_low_alert(self):
        """Test low temperature alert."""
        service = WeatherAlertService()
        service.subscribe("cold_user", 0, 0, "Test")
        sub = service._subscriptions["cold_user"]
        sub.temperature_threshold_low = 32.0

        current = {"temperature": 25}

        alert = service._check_temperature(current, sub)
        assert alert is not None
        assert alert["type"] == "low_temperature"

    def test_no_temperature_alert_normal(self):
        """Test no alert for normal temperature."""
        service = WeatherAlertService()
        service.subscribe("normal_temp_user", 0, 0, "Test")
        sub = service._subscriptions["normal_temp_user"]

        current = {"temperature": 70}

        alert = service._check_temperature(current, sub)
        assert alert is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
