"""Mocked API tests that don't require external network calls."""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

from app.tools.weather import (
    get_current_weather,
    get_weather_forecast,
    get_hourly_forecast,
    _weather_code_to_description,
)
from app.tools.geocoding import geocode_location, reverse_geocode
from app.services.weather_alerts import WeatherAlertService


class TestWeatherToolsMocked:
    """Mocked tests for weather tools."""

    @pytest.mark.asyncio
    async def test_get_current_weather_mocked(self):
        """Test current weather with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "current": {
                "temperature_2m": 72.5,
                "relative_humidity_2m": 65,
                "apparent_temperature": 75.0,
                "is_day": 1,
                "precipitation": 0.0,
                "rain": 0.0,
                "weather_code": 1,
                "cloud_cover": 25,
                "wind_speed_10m": 10.5,
                "wind_direction_10m": 180,
                "wind_gusts_10m": 15.0,
            },
            "timezone": "America/New_York",
            "latitude": 40.71,
            "longitude": -74.01,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await get_current_weather(40.7128, -74.0060)

            assert result["temperature"] == 72.5
            assert result["humidity"] == 65
            assert result["weather_description"] == "Mainly clear"
            assert result["is_day"] is True

    @pytest.mark.asyncio
    async def test_get_weather_forecast_mocked(self):
        """Test weather forecast with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "daily": {
                "time": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "weather_code": [1, 3, 61],
                "temperature_2m_max": [75.0, 72.0, 68.0],
                "temperature_2m_min": [55.0, 52.0, 50.0],
                "apparent_temperature_max": [78.0, 74.0, 70.0],
                "apparent_temperature_min": [52.0, 50.0, 48.0],
                "sunrise": ["07:00", "07:01", "07:02"],
                "sunset": ["17:30", "17:31", "17:32"],
                "precipitation_sum": [0.0, 0.0, 0.5],
                "rain_sum": [0.0, 0.0, 0.5],
                "precipitation_hours": [0, 0, 3],
                "precipitation_probability_max": [10, 20, 80],
                "wind_speed_10m_max": [15.0, 12.0, 20.0],
                "wind_gusts_10m_max": [25.0, 18.0, 30.0],
                "uv_index_max": [6.0, 5.0, 3.0],
            },
            "timezone": "America/New_York",
            "latitude": 40.71,
            "longitude": -74.01,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await get_weather_forecast(40.7128, -74.0060, days=3)

            assert len(result["forecasts"]) == 3
            assert result["forecasts"][0]["temp_high"] == 75.0
            assert result["forecasts"][2]["precipitation_probability"] == 80

    @pytest.mark.asyncio
    async def test_get_hourly_forecast_mocked(self):
        """Test hourly forecast with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "hourly": {
                "time": ["2024-01-15T10:00", "2024-01-15T11:00", "2024-01-15T12:00"],
                "temperature_2m": [68.0, 70.0, 72.0],
                "relative_humidity_2m": [60, 55, 50],
                "apparent_temperature": [70.0, 72.0, 74.0],
                "precipitation_probability": [10, 20, 30],
                "precipitation": [0.0, 0.0, 0.1],
                "rain": [0.0, 0.0, 0.1],
                "weather_code": [1, 2, 61],
                "cloud_cover": [10, 30, 60],
                "wind_speed_10m": [5.0, 8.0, 12.0],
                "wind_gusts_10m": [10.0, 15.0, 20.0],
                "uv_index": [5.0, 6.0, 4.0],
                "is_day": [1, 1, 1],
            },
            "timezone": "America/New_York",
            "latitude": 40.71,
            "longitude": -74.01,
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await get_hourly_forecast(40.7128, -74.0060, hours=3)

            assert len(result["forecasts"]) == 3
            assert result["forecasts"][1]["temperature"] == 70.0


class TestGeocodingToolsMocked:
    """Mocked tests for geocoding tools."""

    @pytest.mark.asyncio
    async def test_geocode_location_mocked(self):
        """Test geocoding with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "lat": "40.7127281",
                "lon": "-74.0060152",
                "display_name": "New York City, New York, USA",
                "name": "New York City",
                "type": "city",
                "address": {
                    "city": "New York City",
                    "state": "New York",
                    "country": "United States",
                    "country_code": "us",
                    "postcode": "10001",
                },
                "boundingbox": ["40.4960", "40.9152", "-74.2591", "-73.7004"],
            }
        ]
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await geocode_location("New York City")

            assert len(result) == 1
            assert result[0]["latitude"] == 40.7127281
            assert result[0]["longitude"] == -74.0060152
            assert result[0]["address"]["city"] == "New York City"

    @pytest.mark.asyncio
    async def test_reverse_geocode_mocked(self):
        """Test reverse geocoding with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "lat": "40.7128",
            "lon": "-74.0060",
            "display_name": "123 Broadway, New York, NY 10006, USA",
            "name": "123 Broadway",
            "address": {
                "house_number": "123",
                "road": "Broadway",
                "neighbourhood": "Financial District",
                "suburb": "Manhattan",
                "city": "New York",
                "county": "New York County",
                "state": "New York",
                "postcode": "10006",
                "country": "United States",
                "country_code": "us",
            },
        }
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient") as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )

            result = await reverse_geocode(40.7128, -74.0060)

            assert result["address"]["city"] == "New York"
            assert result["address"]["country"] == "United States"


class TestWeatherAlertServiceMocked:
    """Mocked tests for weather alert service."""

    @pytest.mark.asyncio
    async def test_check_weather_for_user_mocked(self):
        """Test weather check with mocked API calls."""
        service = WeatherAlertService()
        service.subscribe(
            user_id="mocked_user",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="New York",
        )

        # Mock weather responses
        mock_current = {
            "temperature": 72.0,
            "weather_code": 1,
            "weather_description": "Mainly clear",
            "wind_speed": 10,
            "wind_gusts": 15,
            "precipitation": 0,
        }

        mock_forecast = {
            "forecasts": [
                {"precipitation_probability": 10, "time": "2024-01-15T10:00"},
                {"precipitation_probability": 15, "time": "2024-01-15T11:00"},
            ]
        }

        with patch("app.services.weather_alerts.weather.get_current_weather",
                   new_callable=AsyncMock, return_value=mock_current):
            with patch("app.services.weather_alerts.weather.get_hourly_forecast",
                       new_callable=AsyncMock, return_value=mock_forecast):

                alerts = await service.check_weather_for_user("mocked_user")

                # Should not generate alerts for good weather
                assert isinstance(alerts, list)

                # Verify last_checked was updated
                sub = service._subscriptions["mocked_user"]
                assert sub.last_checked is not None
                assert sub.last_conditions == mock_current

    @pytest.mark.asyncio
    async def test_check_weather_generates_severe_alert(self):
        """Test that severe weather generates an alert."""
        service = WeatherAlertService()
        service.subscribe(
            user_id="severe_test",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="New York",
        )

        # Mock severe weather (thunderstorm)
        mock_current = {
            "temperature": 75.0,
            "weather_code": 95,  # Thunderstorm
            "weather_description": "Thunderstorm",
            "wind_speed": 25,
            "wind_gusts": 40,
            "precipitation": 0.5,
        }

        mock_forecast = {
            "forecasts": [
                {"precipitation_probability": 90, "time": "2024-01-15T10:00"},
            ]
        }

        with patch("app.services.weather_alerts.weather.get_current_weather",
                   new_callable=AsyncMock, return_value=mock_current):
            with patch("app.services.weather_alerts.weather.get_hourly_forecast",
                       new_callable=AsyncMock, return_value=mock_forecast):
                with patch("app.services.weather_alerts.get_notification_service") as mock_notif:
                    mock_notif.return_value.send_weather_alert = AsyncMock(return_value=True)

                    alerts = await service.check_weather_for_user("severe_test")

                    # Should generate a severe weather alert
                    assert len(alerts) >= 1
                    assert any(a["type"] == "severe_weather" for a in alerts)

    @pytest.mark.asyncio
    async def test_check_weather_generates_rain_alert(self):
        """Test that upcoming rain generates an alert."""
        service = WeatherAlertService()
        service.subscribe(
            user_id="rain_test",
            latitude=40.7128,
            longitude=-74.0060,
            location_name="New York",
        )

        # Mock current weather (not raining)
        mock_current = {
            "temperature": 70.0,
            "weather_code": 1,
            "weather_description": "Clear",
            "wind_speed": 10,
            "wind_gusts": 15,
            "precipitation": 0,
        }

        # Mock forecast with high rain probability coming
        mock_forecast = {
            "forecasts": [
                {"precipitation_probability": 20, "time": "2024-01-15T10:00"},
                {"precipitation_probability": 50, "time": "2024-01-15T11:00"},
                {"precipitation_probability": 85, "time": "2024-01-15T12:00"},
            ]
        }

        with patch("app.services.weather_alerts.weather.get_current_weather",
                   new_callable=AsyncMock, return_value=mock_current):
            with patch("app.services.weather_alerts.weather.get_hourly_forecast",
                       new_callable=AsyncMock, return_value=mock_forecast):
                with patch("app.services.weather_alerts.get_notification_service") as mock_notif:
                    mock_notif.return_value.send_weather_alert = AsyncMock(return_value=True)

                    alerts = await service.check_weather_for_user("rain_test")

                    # Should generate a rain alert
                    assert len(alerts) >= 1
                    assert any(a["type"] == "rain_coming" for a in alerts)


class TestWeatherCodeDescriptions:
    """Tests for weather code to description mapping."""

    def test_all_known_codes(self):
        """Test that all known weather codes have descriptions."""
        known_codes = [0, 1, 2, 3, 45, 48, 51, 53, 55, 56, 57, 61, 63, 65,
                       66, 67, 71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99]

        for code in known_codes:
            desc = _weather_code_to_description(code)
            assert desc is not None
            assert "Unknown" not in desc

    def test_unknown_code(self):
        """Test that unknown codes return 'Unknown'."""
        desc = _weather_code_to_description(999)
        assert "Unknown" in desc

    def test_none_code(self):
        """Test handling of None weather code."""
        desc = _weather_code_to_description(None)
        assert desc == "Unknown"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
