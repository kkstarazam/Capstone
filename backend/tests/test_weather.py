"""Tests for weather tools."""
import pytest
import httpx
from app.tools.weather import (
    get_current_weather,
    get_weather_forecast,
    get_hourly_forecast,
    _weather_code_to_description
)


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


@network_required
@pytest.mark.asyncio
async def test_get_current_weather():
    """Test fetching current weather for New York."""
    # New York coordinates
    result = await get_current_weather(
        latitude=40.7128,
        longitude=-74.0060,
        temperature_unit="fahrenheit"
    )

    assert "temperature" in result
    assert "humidity" in result
    assert "weather_description" in result
    assert result["temperature_unit"] == "fahrenheit"


@network_required
@pytest.mark.asyncio
async def test_get_weather_forecast():
    """Test fetching weather forecast."""
    result = await get_weather_forecast(
        latitude=40.7128,
        longitude=-74.0060,
        days=3
    )

    assert "forecasts" in result
    assert len(result["forecasts"]) >= 1
    assert "temp_high" in result["forecasts"][0]
    assert "temp_low" in result["forecasts"][0]


@network_required
@pytest.mark.asyncio
async def test_get_hourly_forecast():
    """Test fetching hourly forecast."""
    result = await get_hourly_forecast(
        latitude=40.7128,
        longitude=-74.0060,
        hours=12
    )

    assert "forecasts" in result
    assert len(result["forecasts"]) >= 1


def test_weather_code_to_description():
    """Test weather code conversion."""
    assert _weather_code_to_description(0) == "Clear sky"
    assert _weather_code_to_description(3) == "Overcast"
    assert _weather_code_to_description(95) == "Thunderstorm"
    assert "Unknown" in _weather_code_to_description(999)
