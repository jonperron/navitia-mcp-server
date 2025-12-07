"""Get arrivals tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.arrival import ArrivalRequest

from .formatters import format_departure
from .utils import parse_iso_datetime


def get_tool() -> Tool:
    """Get the get_arrivals tool definition."""
    return Tool(
        name="get_arrivals",
        description="Get upcoming arrivals at a transit stop with real-time information. REQUIRES a stop_id. If you only have a place name, use find_places first to get the stop_id.",
        inputSchema={
            "type": "object",
            "properties": {
                "stop_id": {
                    "type": "string",
                    "description": "Stop area or stop point ID",
                },
                "region_id": {
                    "type": "string",
                    "description": "Region ID",
                },
                "from_datetime": {
                    "type": "string",
                    "description": "Start datetime for arrivals in ISO format",
                },
                "duration": {
                    "type": "integer",
                    "description": "Time window in seconds (default: 3600)",
                },
            },
            "required": ["stop_id", "region_id"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the get_arrivals tool call."""
    # Parse datetime if provided
    dt = None
    if "from_datetime" in arguments:
        dt = parse_iso_datetime(arguments["from_datetime"])

    # Create request
    request = ArrivalRequest(
        from_datetime=dt.isoformat() if dt else None,
        duration=arguments.get("duration", 3600),
    )

    stop_id = arguments["stop_id"]

    arrivals = navitia_client.arrivals.list_arrivals_by_region_id_and_path(
        region_id=arguments["region_id"],
        resource_path=stop_id,
        request=request,
    )

    results = [format_departure(a) for a in arrivals]  # Same format as departures

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
