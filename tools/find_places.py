"""Find places tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.place import PlaceRequest

from .formatters import format_place


def get_tool() -> Tool:
    """Get the find_places tool definition."""
    return Tool(
        name="find_places",
        description="Search for transit stops, addresses, and points of interest. Use this FIRST when you need to find stop IDs for other operations like find_journey, get_departures, or find_nearby_places. Returns IDs in format 'stop_area:XXX' or 'stop_point:XXX' that can be used in other tools.",
        inputSchema={
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'Gare de Lyon', 'Eiffel Tower')",
                },
                "region_id": {
                    "type": "string",
                    "description": "Limit search to specific region (e.g., 'fr-idf')",
                },
                "type": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Types to search for: 'stop_area', 'stop_point', 'address', 'poi', 'administrative_region'",
                },
            },
            "required": ["query", "region_id"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the find_places tool call."""
    request = PlaceRequest(
        query=arguments["query"],
        type=tuple(arguments.get("type", [])),
    )

    # Use places API
    places = navitia_client.places.list_places(
        region_id=arguments["region_id"],
        request=request,
    )

    results = [format_place(p) for p in places]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
