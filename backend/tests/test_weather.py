"""Tests for weather tools."""
import pytest
from app.tools.weather import (
    get_current_weather,
    get_weather_forecast,
    get_hourly_forecast,
    _weather_code_to_description
)


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
