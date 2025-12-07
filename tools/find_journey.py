"""Find journey tool."""

import json
from datetime import datetime
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.journey import JourneyRequest

from .formatters import format_journey
from .utils import parse_iso_datetime


def get_tool() -> Tool:
    """Get the find_journey tool definition."""
    return Tool(
        name="find_journey",
        description="Find a transit journey between two locations with real-time data. Returns route options with transfers, durations, and departure/arrival times. IMPORTANT: If you don't have stop IDs, use find_places first to search for locations and get their IDs (e.g., 'stop_area:RAT:SA:GDLYO').",
        inputSchema={
            "type": "object",
            "properties": {
                "from_location": {
                    "type": "string",
                    "description": "Starting point (stop ID like 'stop_area:XXX', address, or coordinates 'lon;lat')",
                },
                "to_location": {
                    "type": "string",
                    "description": "Destination (stop ID, address, or coordinates)",
                },
                "datetime": {
                    "type": "string",
                    "description": "Departure/arrival datetime in ISO format (e.g., '2024-06-01T08:00:00'). Defaults to now.",
                },
                "datetime_represents": {
                    "type": "string",
                    "enum": ["departure", "arrival"],
                    "description": "Whether datetime is for departure or arrival (default: departure)",
                },
                "region_id": {
                    "type": "string",
                    "description": "Specific region to search in (e.g., 'fr-idf' for Paris region)",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of journey options to return (default: 5)",
                    "minimum": 1,
                    "maximum": 20,
                },
            },
            "required": ["from_location", "to_location"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the find_journey tool call."""
    # Parse datetime if provided
    dt = None
    if "datetime" in arguments:
        dt = parse_iso_datetime(arguments["datetime"])
    else:
        dt = datetime.now()

    # Create journey request
    request = JourneyRequest(
        from_=arguments["from_location"],
        to_=arguments["to_location"],
        datetime_=dt,
        datetime_represents=arguments.get("datetime_represents", "departure"),
        count=arguments.get("count", 5),
    )

    # Get journeys
    if "region_id" in arguments:
        journeys = navitia_client.journeys.list_journeys_with_region_id(
            region_id=arguments["region_id"],
            request=request,
        )
    else:
        journeys = navitia_client.journeys.list_journeys(request=request)

    # Format results
    results = [format_journey(j) for j in journeys]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
