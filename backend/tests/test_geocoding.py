"""Tests for geocoding tools."""
import pytest
import httpx
from app.tools.geocoding import geocode_location, reverse_geocode


def network_available():
    """Check if external network is available."""
    try:
        httpx.get("https://nominatim.openstreetmap.org/status", timeout=5)
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
async def test_geocode_location():
    """Test geocoding a city name."""
    results = await geocode_location("New York City", limit=3)

    assert len(results) >= 1
    assert "latitude" in results[0]
    assert "longitude" in results[0]
    assert "display_name" in results[0]

    # Check coordinates are roughly correct for NYC
    assert 40 < results[0]["latitude"] < 41
    assert -75 < results[0]["longitude"] < -73


@network_required
@pytest.mark.asyncio
async def test_reverse_geocode():
    """Test reverse geocoding coordinates."""
    # Empire State Building coordinates
    result = await reverse_geocode(
        latitude=40.7484,
        longitude=-73.9857
    )

    assert "display_name" in result
    assert "address" in result
    assert result["address"]["country"] == "United States"
