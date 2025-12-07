"""Get coverage tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient


def get_tool() -> Tool:
    """Get the get_coverage tool definition."""
    return Tool(
        name="get_coverage",
        description="Get list of regions covered by the Navitia API. Use this to discover available region IDs.",
        inputSchema={
            "type": "object",
            "properties": {},
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the get_coverage tool call."""
    regions = navitia_client.coverage.list_coverage_regions()

    results = [
        {
            "id": region.id,
            "name": region.name,
            "status": region.status,
            "shape": region.shape if hasattr(region, "shape") else None,
        }
        for region in regions
    ]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
