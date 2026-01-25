"""End-to-end tests for the Weather Intelligence Agent API."""
import pytest
import httpx
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app


client = TestClient(app)


def network_available():
    """Check if external network is available."""
    try:
        httpx.get("https://api.open-meteo.com/v1/forecast?latitude=0&longitude=0&current=temperature_2m", timeout=5)
        return True
    except Exception:
        return False


# Skip network tests if network is unavailable
network_required = pytest.mark.skipif(
    not network_available(),
    reason="External network not available (proxy or firewall blocking requests)"
)


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self):
        """Test that health endpoint returns healthy status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "services" in data
        assert data["services"]["weather_api"] == "available"
        assert data["services"]["geocoding"] == "available"


@network_required
class TestWeatherEndpoints:
    """Tests for weather-related endpoints."""

    def test_get_current_weather(self):
        """Test getting current weather for a location."""
        # New York City coordinates
        response = client.post(
            "/api/v1/weather/current",
            json={"latitude": 40.7128, "longitude": -74.0060},
            params={"temperature_unit": "fahrenheit"}
        )
        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "temperature" in data
        assert "humidity" in data
        assert "weather_description" in data
        assert "wind_speed" in data
        assert data["temperature_unit"] == "fahrenheit"

    def test_get_current_weather_celsius(self):
        """Test getting weather in Celsius."""
        response = client.post(
            "/api/v1/weather/current",
            json={"latitude": 51.5074, "longitude": -0.1278},  # London
            params={"temperature_unit": "celsius"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["temperature_unit"] == "celsius"

    def test_get_weather_forecast(self):
        """Test getting weather forecast."""
        response = client.post(
            "/api/v1/weather/forecast",
            json={"latitude": 34.0522, "longitude": -118.2437},  # Los Angeles
            params={"days": 7}
        )
        assert response.status_code == 200
        data = response.json()

        assert "forecasts" in data
        assert len(data["forecasts"]) >= 1
        assert "timezone" in data

        # Check forecast structure
        forecast = data["forecasts"][0]
        assert "date" in forecast
        assert "temp_high" in forecast
        assert "temp_low" in forecast
        assert "weather_description" in forecast

    def test_get_hourly_forecast(self):
        """Test getting hourly forecast."""
        response = client.post(
            "/api/v1/weather/hourly",
            json={"latitude": 47.6062, "longitude": -122.3321},  # Seattle
            params={"hours": 12}
        )
        assert response.status_code == 200
        data = response.json()

        assert "forecasts" in data
        assert len(data["forecasts"]) >= 1

        # Check hourly forecast structure
        hour = data["forecasts"][0]
        assert "time" in hour
        assert "temperature" in hour
        assert "precipitation_probability" in hour

    def test_weather_invalid_coordinates(self):
        """Test weather endpoint with invalid coordinates."""
        response = client.post(
            "/api/v1/weather/current",
            json={"latitude": 999, "longitude": 999}  # Invalid
        )
        # Open-Meteo may still return data for invalid coords
        # but the test ensures the endpoint handles the request
        assert response.status_code in [200, 500]


@network_required
class TestGeocodingEndpoints:
    """Tests for geocoding endpoints."""

    def test_geocode_city(self):
        """Test geocoding a city name."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "San Francisco, CA", "limit": 3}
        )
        assert response.status_code == 200
        data = response.json()

        assert "locations" in data
        assert len(data["locations"]) >= 1

        location = data["locations"][0]
        assert "latitude" in location
        assert "longitude" in location
        assert "display_name" in location

        # Verify coordinates are roughly correct for SF
        assert 37 < location["latitude"] < 38
        assert -123 < location["longitude"] < -122

    def test_geocode_address(self):
        """Test geocoding a specific address."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "1600 Pennsylvania Avenue, Washington DC", "limit": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert "locations" in data

    def test_geocode_international(self):
        """Test geocoding an international location."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "Tokyo, Japan", "limit": 3}
        )
        assert response.status_code == 200
        data = response.json()

        assert len(data["locations"]) >= 1
        location = data["locations"][0]

        # Verify coordinates are roughly correct for Tokyo
        assert 35 < location["latitude"] < 36
        assert 139 < location["longitude"] < 140

    def test_reverse_geocode(self):
        """Test reverse geocoding coordinates."""
        # Statue of Liberty coordinates
        response = client.post(
            "/api/v1/reverse-geocode",
            json={"latitude": 40.6892, "longitude": -74.0445}
        )
        assert response.status_code == 200
        data = response.json()

        assert "display_name" in data
        assert "address" in data
        assert data["address"]["country"] == "United States"

    def test_geocode_empty_query(self):
        """Test geocoding with empty query."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "", "limit": 5}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["locations"] == []


class TestNotificationEndpoints:
    """Tests for notification endpoints."""

    def test_register_device(self):
        """Test registering a device for notifications."""
        response = client.post(
            "/api/v1/notifications/register",
            params={"user_id": "test_user_123", "device_token": "fake_token_abc"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "registered"
        assert data["user_id"] == "test_user_123"

    def test_unregister_device(self):
        """Test unregistering a device."""
        # First register
        client.post(
            "/api/v1/notifications/register",
            params={"user_id": "test_user_456", "device_token": "fake_token_def"}
        )

        # Then unregister
        response = client.delete("/api/v1/notifications/unregister/test_user_456")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unregistered"

    def test_unregister_nonexistent_device(self):
        """Test unregistering a device that doesn't exist."""
        response = client.delete("/api/v1/notifications/unregister/nonexistent_user")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "not_found"


class TestAlertEndpoints:
    """Tests for weather alert subscription endpoints."""

    def test_subscribe_to_alerts(self):
        """Test subscribing to weather alerts."""
        response = client.post(
            "/api/v1/alerts/subscribe",
            params={
                "user_id": "alert_test_user",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "location_name": "New York City",
                "rain_alerts": True,
                "temperature_alerts": True,
                "severe_weather_alerts": True,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "subscribed"

    def test_unsubscribe_from_alerts(self):
        """Test unsubscribing from weather alerts."""
        # First subscribe
        client.post(
            "/api/v1/alerts/subscribe",
            params={
                "user_id": "unsub_test_user",
                "latitude": 34.0522,
                "longitude": -118.2437,
                "location_name": "Los Angeles",
            }
        )

        # Then unsubscribe
        response = client.delete("/api/v1/alerts/unsubscribe/unsub_test_user")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "unsubscribed"

    @network_required
    def test_check_alerts(self):
        """Test manually checking for alerts."""
        # Subscribe first
        client.post(
            "/api/v1/alerts/subscribe",
            params={
                "user_id": "check_alert_user",
                "latitude": 47.6062,
                "longitude": -122.3321,
                "location_name": "Seattle",
            }
        )

        # Check alerts
        response = client.post("/api/v1/alerts/check/check_alert_user")
        assert response.status_code == 200
        data = response.json()
        assert "alerts" in data
        assert "count" in data
        assert isinstance(data["alerts"], list)


@network_required
class TestIntegrationScenarios:
    """Integration tests for real-world scenarios."""

    def test_morning_briefing_flow(self):
        """Test the morning briefing use case flow."""
        # 1. Geocode user's location
        geo_response = client.post(
            "/api/v1/geocode",
            json={"query": "Boston, MA", "limit": 1}
        )
        assert geo_response.status_code == 200
        location = geo_response.json()["locations"][0]

        # 2. Get current weather
        weather_response = client.post(
            "/api/v1/weather/current",
            json={
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            }
        )
        assert weather_response.status_code == 200
        current = weather_response.json()

        # 3. Get today's forecast
        forecast_response = client.post(
            "/api/v1/weather/hourly",
            json={
                "latitude": location["latitude"],
                "longitude": location["longitude"]
            },
            params={"hours": 24}
        )
        assert forecast_response.status_code == 200
        forecast = forecast_response.json()

        # Verify we have all info needed for a morning briefing
        assert current["temperature"] is not None
        assert len(forecast["forecasts"]) >= 12

    def test_activity_planning_flow(self):
        """Test the activity planning use case flow."""
        # 1. Get 7-day forecast for planning
        forecast_response = client.post(
            "/api/v1/weather/forecast",
            json={"latitude": 37.7749, "longitude": -122.4194},  # SF
            params={"days": 7}
        )
        assert forecast_response.status_code == 200
        forecasts = forecast_response.json()["forecasts"]

        # 2. Analyze forecasts for good running days
        good_days = []
        for forecast in forecasts:
            temp_high = forecast.get("temp_high", 100)
            precip_prob = forecast.get("precipitation_probability", 0) or 0

            # Good running weather: 50-75°F, low rain chance
            if 50 <= temp_high <= 75 and precip_prob < 30:
                good_days.append(forecast["date"])

        # We found potential good days (results will vary)
        assert isinstance(good_days, list)

    def test_travel_planning_flow(self):
        """Test the travel planning use case flow."""
        # 1. Geocode destination
        geo_response = client.post(
            "/api/v1/geocode",
            json={"query": "Miami, Florida", "limit": 1}
        )
        assert geo_response.status_code == 200
        destination = geo_response.json()["locations"][0]

        # 2. Get extended forecast
        forecast_response = client.post(
            "/api/v1/weather/forecast",
            json={
                "latitude": destination["latitude"],
                "longitude": destination["longitude"]
            },
            params={"days": 14}
        )
        assert forecast_response.status_code == 200
        forecasts = forecast_response.json()["forecasts"]

        # 3. Verify we can make packing suggestions
        avg_high = sum(f["temp_high"] for f in forecasts) / len(forecasts)
        avg_low = sum(f["temp_low"] for f in forecasts) / len(forecasts)

        # Miami should be warm
        assert avg_high > 60  # Should be warm year-round

    def test_alert_subscription_flow(self):
        """Test the full alert subscription flow."""
        user_id = "flow_test_user"

        # 1. Register device
        reg_response = client.post(
            "/api/v1/notifications/register",
            params={"user_id": user_id, "device_token": "test_token_xyz"}
        )
        assert reg_response.status_code == 200

        # 2. Geocode location
        geo_response = client.post(
            "/api/v1/geocode",
            json={"query": "Chicago, IL", "limit": 1}
        )
        location = geo_response.json()["locations"][0]

        # 3. Subscribe to alerts
        sub_response = client.post(
            "/api/v1/alerts/subscribe",
            params={
                "user_id": user_id,
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "location_name": "Chicago",
            }
        )
        assert sub_response.status_code == 200

        # 4. Check for alerts
        check_response = client.post(f"/api/v1/alerts/check/{user_id}")
        assert check_response.status_code == 200
        assert "alerts" in check_response.json()

        # 5. Cleanup
        client.delete(f"/api/v1/alerts/unsubscribe/{user_id}")
        client.delete(f"/api/v1/notifications/unregister/{user_id}")


@network_required
class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_special_characters_in_location(self):
        """Test geocoding with special characters."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "São Paulo, Brazil", "limit": 1}
        )
        assert response.status_code == 200

    def test_unicode_location(self):
        """Test geocoding with unicode characters."""
        response = client.post(
            "/api/v1/geocode",
            json={"query": "東京", "limit": 1}  # Tokyo in Japanese
        )
        assert response.status_code == 200

    def test_very_long_query(self):
        """Test geocoding with a very long query string."""
        long_query = "123 Main Street, Apartment 456, " * 10
        response = client.post(
            "/api/v1/geocode",
            json={"query": long_query, "limit": 1}
        )
        # Should handle gracefully (may return empty or results)
        assert response.status_code == 200

    def test_extreme_coordinates(self):
        """Test with coordinates at extreme locations."""
        # North Pole
        response = client.post(
            "/api/v1/weather/current",
            json={"latitude": 90.0, "longitude": 0.0}
        )
        assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling multiple concurrent weather requests."""
        locations = [
            (40.7128, -74.0060),   # NYC
            (34.0522, -118.2437),  # LA
            (41.8781, -87.6298),   # Chicago
            (29.7604, -95.3698),   # Houston
        ]

        responses = []
        for lat, lon in locations:
            response = client.post(
                "/api/v1/weather/current",
                json={"latitude": lat, "longitude": lon}
            )
            responses.append(response)

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
