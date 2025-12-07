"""Find nearby places tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.places_nearby import PlacesNearbyRequest

from .formatters import format_place


def get_tool() -> Tool:
    """Get the find_nearby_places tool definition."""
    return Tool(
        name="find_nearby_places",
        description="Find transit stops and places near a specific location. Useful for discovering transit options in an area. If you don't have a stop ID for the location parameter, use find_places first to search for the location.",
        inputSchema={
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "Location (stop ID, address, or coordinates 'lon;lat')",
                },
                "region_id": {
                    "type": "string",
                    "description": "Region to search in",
                },
                "distance": {
                    "type": "integer",
                    "description": "Search radius in meters (default: 500)",
                    "minimum": 100,
                    "maximum": 5000,
                },
                "type": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types to find (default: ['stop_area', 'stop_point'])",
                },
            },
            "required": ["location"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the find_nearby_places tool call."""
    # Create request
    request = PlacesNearbyRequest(
        distance=arguments.get("distance", 500),
        type=tuple(arguments.get("type", ["stop_area", "stop_point"])),
    )

    location = arguments["location"]

    # Try to parse as coordinates
    if ";" in location:
        parts = location.split(";")
        if len(parts) != 2:
            return [
                TextContent(
                    type="text",
                    text="Error: location must be in 'lon;lat' format for coordinates",
                )
            ]
        try:
            lon, lat = float(parts[0]), float(parts[1])
        except ValueError:
            return [
                TextContent(
                    type="text",
                    text="Error: Invalid coordinate format. Expected numeric 'lon;lat' values",
                )
            ]

        places, _ = (
            navitia_client.places_nearby.list_objects_by_object_coordinates_only(
                lon=lon,
                lat=lat,
                request=request,
            )
        )
    else:
        # Use as resource path
        if "region_id" not in arguments:
            return [
                TextContent(
                    type="text",
                    text="Error: region_id is required when location is not provided as coordinates",
                )
            ]

        places, _ = navitia_client.places_nearby.list_objects_by_region_id_and_path(
            region_id=arguments["region_id"],
            resource_path=location,
            request=request,
        )

    results = [format_place(p) for p in places]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
