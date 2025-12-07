"""Get line reports tool."""

import json
from typing import Sequence

from mcp.types import Tool, TextContent
from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.line_report import LineReportRequest


def get_tool() -> Tool:
    """Get the get_line_reports tool definition."""
    return Tool(
        name="get_line_reports",
        description="Get service status and disruption information for transit lines in a region. To check a specific line, provide its resource_path (e.g., 'lines/line:RAT:M1'). Use find_places or get_coverage first if you need to discover region IDs or line IDs.",
        inputSchema={
            "type": "object",
            "properties": {
                "region_id": {
                    "type": "string",
                    "description": "Region ID (e.g., 'fr-idf')",
                },
                "resource_path": {
                    "type": "string",
                    "description": "Optional path to specific line (e.g., 'lines/line:RAT:M1')",
                },
            },
            "required": ["region_id"],
        },
    )


async def handle(
    navitia_client: NavitiaClient, arguments: dict
) -> Sequence[TextContent]:
    """Handle the get_line_reports tool call."""
    request = LineReportRequest()

    resource_path = arguments.get("resource_path", "")

    reports = navitia_client.line_reports.list_line_reports(
        request=request,
        region_id=arguments["region_id"],
        resource_path=resource_path,
    )

    results = [
        {
            "line": {
                "id": report.line.id if report.line else None,
                "name": report.line.name if report.line else None,
                "code": report.line.code if report.line else None,
            },
            "pt_objects": (
                [
                    {
                        "id": obj.id,
                        "name": obj.name if hasattr(obj, "name") else None,
                    }
                    for obj in report.pt_objects
                ]
                if report.pt_objects
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
