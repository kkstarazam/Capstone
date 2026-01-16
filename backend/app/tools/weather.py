"""Open-Meteo Weather API tool for Letta agent.

Open-Meteo is a free, open-source weather API that requires no API key.
https://open-meteo.com/
"""
import httpx
from typing import Optional
from datetime import datetime, timedelta


OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1"


async def get_current_weather(
    latitude: float,
    longitude: float,
    temperature_unit: str = "fahrenheit"
) -> dict:
    """
    Get current weather conditions for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        temperature_unit: "fahrenheit" or "celsius"

    Returns:
        Dictionary with current weather data including temperature,
        conditions, humidity, wind speed, and more.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "is_day",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ],
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        response.raise_for_status()
        data = response.json()

    current = data.get("current", {})

    return {
        "temperature": current.get("temperature_2m"),
        "feels_like": current.get("apparent_temperature"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "rain": current.get("rain"),
        "cloud_cover": current.get("cloud_cover"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_direction": current.get("wind_direction_10m"),
        "wind_gusts": current.get("wind_gusts_10m"),
        "is_day": current.get("is_day") == 1,
        "weather_code": current.get("weather_code"),
        "weather_description": _weather_code_to_description(current.get("weather_code")),
        "temperature_unit": temperature_unit,
        "timezone": data.get("timezone"),
        "location": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }
    }


async def get_weather_forecast(
    latitude: float,
    longitude: float,
    days: int = 7,
    temperature_unit: str = "fahrenheit"
) -> dict:
    """
    Get weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        days: Number of forecast days (1-16)
        temperature_unit: "fahrenheit" or "celsius"

    Returns:
        Dictionary with daily forecast data.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "daily": [
            "weather_code",
            "temperature_2m_max",
            "temperature_2m_min",
            "apparent_temperature_max",
            "apparent_temperature_min",
            "sunrise",
            "sunset",
            "precipitation_sum",
            "rain_sum",
            "precipitation_hours",
            "precipitation_probability_max",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "uv_index_max",
        ],
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
        "forecast_days": min(days, 16),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        response.raise_for_status()
        data = response.json()

    daily = data.get("daily", {})
    dates = daily.get("time", [])

    forecasts = []
    for i, date in enumerate(dates):
        forecasts.append({
            "date": date,
            "weather_code": daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else None,
            "weather_description": _weather_code_to_description(
                daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else None
            ),
            "temp_high": daily.get("temperature_2m_max", [])[i] if i < len(daily.get("temperature_2m_max", [])) else None,
            "temp_low": daily.get("temperature_2m_min", [])[i] if i < len(daily.get("temperature_2m_min", [])) else None,
            "feels_like_high": daily.get("apparent_temperature_max", [])[i] if i < len(daily.get("apparent_temperature_max", [])) else None,
            "feels_like_low": daily.get("apparent_temperature_min", [])[i] if i < len(daily.get("apparent_temperature_min", [])) else None,
            "sunrise": daily.get("sunrise", [])[i] if i < len(daily.get("sunrise", [])) else None,
            "sunset": daily.get("sunset", [])[i] if i < len(daily.get("sunset", [])) else None,
            "precipitation": daily.get("precipitation_sum", [])[i] if i < len(daily.get("precipitation_sum", [])) else None,
            "precipitation_probability": daily.get("precipitation_probability_max", [])[i] if i < len(daily.get("precipitation_probability_max", [])) else None,
            "precipitation_hours": daily.get("precipitation_hours", [])[i] if i < len(daily.get("precipitation_hours", [])) else None,
            "wind_speed_max": daily.get("wind_speed_10m_max", [])[i] if i < len(daily.get("wind_speed_10m_max", [])) else None,
            "wind_gusts_max": daily.get("wind_gusts_10m_max", [])[i] if i < len(daily.get("wind_gusts_10m_max", [])) else None,
            "uv_index_max": daily.get("uv_index_max", [])[i] if i < len(daily.get("uv_index_max", [])) else None,
        })

    return {
        "forecasts": forecasts,
        "temperature_unit": temperature_unit,
        "timezone": data.get("timezone"),
        "location": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }
    }


async def get_hourly_forecast(
    latitude: float,
    longitude: float,
    hours: int = 24,
    temperature_unit: str = "fahrenheit"
) -> dict:
    """
    Get hourly weather forecast for a location.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location
        hours: Number of hours to forecast (max 384 = 16 days)
        temperature_unit: "fahrenheit" or "celsius"

    Returns:
        Dictionary with hourly forecast data.
    """
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation_probability",
            "precipitation",
            "rain",
            "weather_code",
            "cloud_cover",
            "wind_speed_10m",
            "wind_gusts_10m",
            "uv_index",
            "is_day",
        ],
        "temperature_unit": temperature_unit,
        "wind_speed_unit": "mph",
        "precipitation_unit": "inch",
        "timezone": "auto",
        "forecast_hours": min(hours, 384),
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{OPEN_METEO_BASE_URL}/forecast", params=params)
        response.raise_for_status()
        data = response.json()

    hourly = data.get("hourly", {})
    times = hourly.get("time", [])[:hours]

    forecasts = []
    for i, time in enumerate(times):
        forecasts.append({
            "time": time,
            "temperature": hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else None,
            "feels_like": hourly.get("apparent_temperature", [])[i] if i < len(hourly.get("apparent_temperature", [])) else None,
            "humidity": hourly.get("relative_humidity_2m", [])[i] if i < len(hourly.get("relative_humidity_2m", [])) else None,
            "precipitation_probability": hourly.get("precipitation_probability", [])[i] if i < len(hourly.get("precipitation_probability", [])) else None,
            "precipitation": hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else None,
            "weather_code": hourly.get("weather_code", [])[i] if i < len(hourly.get("weather_code", [])) else None,
            "weather_description": _weather_code_to_description(
                hourly.get("weather_code", [])[i] if i < len(hourly.get("weather_code", [])) else None
            ),
            "cloud_cover": hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else None,
            "wind_speed": hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else None,
            "wind_gusts": hourly.get("wind_gusts_10m", [])[i] if i < len(hourly.get("wind_gusts_10m", [])) else None,
            "uv_index": hourly.get("uv_index", [])[i] if i < len(hourly.get("uv_index", [])) else None,
            "is_day": hourly.get("is_day", [])[i] == 1 if i < len(hourly.get("is_day", [])) else None,
        })

    return {
        "forecasts": forecasts,
        "temperature_unit": temperature_unit,
        "timezone": data.get("timezone"),
        "location": {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
        }
    }


def _weather_code_to_description(code: Optional[int]) -> str:
    """Convert WMO weather code to human-readable description."""
    if code is None:
        return "Unknown"

    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snowfall",
        73: "Moderate snowfall",
        75: "Heavy snowfall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail",
    }

    return weather_codes.get(code, f"Unknown ({code})")
