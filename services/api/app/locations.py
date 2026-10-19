"""Small, privacy-conscious city lookup adapter for birth-location forms."""

from typing import Any

import httpx

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"


def normalise_locations(payload: dict[str, Any]) -> list[dict[str, str | float]]:
    """Keep only the birth-chart fields the frontend needs from a provider response."""
    locations = []
    for item in payload.get("results", []):
        if not isinstance(item, dict):
            continue
        name, timezone = item.get("name"), item.get("timezone")
        latitude, longitude = item.get("latitude"), item.get("longitude")
        if not isinstance(name, str) or not isinstance(timezone, str) or not isinstance(latitude, (int, float)) or not isinstance(longitude, (int, float)):
            continue
        parts = [name, item.get("admin1"), item.get("country")]
        label = ", ".join(part for index, part in enumerate(parts) if isinstance(part, str) and part and part not in parts[:index])
        locations.append({"label": label, "latitude": round(float(latitude), 6), "longitude": round(float(longitude), 6), "timezone": timezone})
    return locations


async def search_locations(query: str) -> list[dict[str, str | float]]:
    """Search a city name without storing a location query or profile data."""
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.get(GEOCODING_URL, params={"name": query, "count": 6, "language": "en", "format": "json"})
            response.raise_for_status()
    except httpx.HTTPError as exc:
        raise ValueError("Location search is temporarily unavailable. Enter coordinates manually or try again.") from exc
    try:
        return normalise_locations(response.json())
    except (ValueError, AttributeError) as exc:
        raise ValueError("Location search returned an invalid response. Please try again.") from exc
