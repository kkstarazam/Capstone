"""Geocoding tool using Nominatim (OpenStreetMap) - completely free.

Nominatim is a free geocoding service powered by OpenStreetMap data.
https://nominatim.org/
"""
import httpx
from typing import Optional, List


NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"

# Required by Nominatim's usage policy
HEADERS = {
    "User-Agent": "WeatherIntelligenceAgent/1.0"
}


async def geocode_location(
    query: str,
    limit: int = 5
) -> List[dict]:
    """
    Convert an address or place name to coordinates.

    Args:
        query: Address, city name, or place to search for
        limit: Maximum number of results to return

    Returns:
        List of matching locations with coordinates and details.
    """
    params = {
        "q": query,
        "format": "json",
        "addressdetails": 1,
        "limit": limit,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NOMINATIM_BASE_URL}/search",
            params=params,
            headers=HEADERS
        )
        response.raise_for_status()
        results = response.json()

    locations = []
    for result in results:
        address = result.get("address", {})
        locations.append({
            "latitude": float(result.get("lat", 0)),
            "longitude": float(result.get("lon", 0)),
            "display_name": result.get("display_name"),
            "name": result.get("name"),
            "type": result.get("type"),
            "address": {
                "city": address.get("city") or address.get("town") or address.get("village"),
                "state": address.get("state"),
                "country": address.get("country"),
                "country_code": address.get("country_code"),
                "postcode": address.get("postcode"),
            },
            "bounding_box": result.get("boundingbox"),
        })

    return locations


async def reverse_geocode(
    latitude: float,
    longitude: float
) -> dict:
    """
    Convert coordinates to an address/place name.

    Args:
        latitude: Latitude of the location
        longitude: Longitude of the location

    Returns:
        Dictionary with address details for the coordinates.
    """
    params = {
        "lat": latitude,
        "lon": longitude,
        "format": "json",
        "addressdetails": 1,
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{NOMINATIM_BASE_URL}/reverse",
            params=params,
            headers=HEADERS
        )
        response.raise_for_status()
        result = response.json()

    address = result.get("address", {})

    return {
        "latitude": float(result.get("lat", latitude)),
        "longitude": float(result.get("lon", longitude)),
        "display_name": result.get("display_name"),
        "name": result.get("name"),
        "address": {
            "house_number": address.get("house_number"),
            "road": address.get("road"),
            "neighbourhood": address.get("neighbourhood"),
            "suburb": address.get("suburb"),
            "city": address.get("city") or address.get("town") or address.get("village"),
            "county": address.get("county"),
            "state": address.get("state"),
            "postcode": address.get("postcode"),
            "country": address.get("country"),
            "country_code": address.get("country_code"),
        },
    }


async def get_location_suggestions(
    partial_query: str,
    limit: int = 5
) -> List[dict]:
    """
    Get location suggestions for autocomplete functionality.

    Args:
        partial_query: Partial address or place name
        limit: Maximum number of suggestions

    Returns:
        List of suggested locations.
    """
    # Nominatim works well for autocomplete with partial queries
    return await geocode_location(partial_query, limit=limit)
