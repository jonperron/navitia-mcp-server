"""Get traffic reports tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.traffic_report import TrafficReportRequest


def get_tool() -> Tool:
    """Get the get_traffic_reports tool definition."""
    return Tool(
        name="get_traffic_reports",
        description="Get current traffic reports and service disruptions for a region.",
        inputSchema={
            "type": "object",
            "properties": {
                "region_id": {
                    "type": "string",
                    "description": "Region ID (e.g., 'fr-idf')",
                },
            },
            "required": ["region_id"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the get_traffic_reports tool call."""
    request = TrafficReportRequest()

    reports = navitia_client.traffic_reports.list_traffic_reports(
        request=request,
        region_id=arguments["region_id"],
    )

    results = [
        {
            "network": {
                "id": report.network.id if report.network else None,
                "name": report.network.name if report.network else None,
            },
            "lines": (
                [
                    {
                        "id": line.id,
                        "name": line.name if hasattr(line, "name") else None,
                    }
                    for line in report.lines
                ]
                if report.lines
                else []
            ),
        }
        for report in reports
    ]

    return [
        TextContent(
            type="text",
            text=json.dumps(results, indent=2),
        )
    ]
