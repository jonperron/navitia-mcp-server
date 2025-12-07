"""Get departures tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.departure import DepartureRequest

from .formatters import format_departure
from .utils import parse_iso_datetime


def get_tool() -> Tool:
    """Get the get_departures tool definition."""
    return Tool(
        name="get_departures",
        description="Get upcoming departures from a transit stop with real-time information. Shows delays and disruptions. REQUIRES a stop_id (e.g., 'stop_area:RAT:SA:GDLYO'). If you only have a place name, use find_places first to get the stop_id.",
        inputSchema={
            "type": "object",
            "properties": {
                "stop_id": {
                    "type": "string",
                    "description": "Stop area or stop point ID (e.g., 'stop_area:RAT:SA:GDLYO')",
                },
                "region_id": {
                    "type": "string",
                    "description": "Region ID (e.g., 'fr-idf')",
                },
                "from_datetime": {
                    "type": "string",
                    "description": "Start datetime for departures in ISO format",
                },
                "duration": {
                    "type": "integer",
                    "description": "Time window in seconds (default: 3600 = 1 hour)",
                },
            },
            "required": ["stop_id", "region_id"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the get_departures tool call."""
    # Parse datetime if provided
    dt = None
    if "from_datetime" in arguments:
        dt = parse_iso_datetime(arguments["from_datetime"])

    # Create request
    request = DepartureRequest(
        from_datetime=dt.isoformat() if dt else None,
        duration=arguments.get("duration", 3600),
    )

    stop_id = arguments["stop_id"]

    departures = navitia_client.departures.list_departures_by_region_id_and_path(
        region_id=arguments["region_id"],
        resource_path=stop_id,
        request=request,
    )

    results = [format_departure(d) for d in departures]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
