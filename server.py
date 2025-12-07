#!/usr/bin/env python3
"""
Navitia MCP Server

A Model Context Protocol server that provides access to real-time transit information
through the Navitia API.
"""

import os
from typing import Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from navitia_client.client.navitia_client import NavitiaClient

from tools import (
    find_journey,
    find_places,
    find_nearby_places,
    get_departures,
    get_arrivals,
    get_coverage,
    get_line_reports,
    get_traffic_reports,
)


# Initialize Navitia client
NAVITIA_TOKEN = os.getenv("NAVITIA_API_TOKEN")
if not NAVITIA_TOKEN:
    raise ValueError("NAVITIA_API_TOKEN environment variable must be set")

navitia_client = NavitiaClient(auth_token=NAVITIA_TOKEN)

# Initialize MCP server
server = Server("navitia-mcp-server")

# Tool handler mapping
TOOL_HANDLERS = {
    "find_journey": find_journey.handle,
    "find_places": find_places.handle,
    "find_nearby_places": find_nearby_places.handle,
    "get_departures": get_departures.handle,
    "get_arrivals": get_arrivals.handle,
    "get_coverage": get_coverage.handle,
    "get_line_reports": get_line_reports.handle,
    "get_traffic_reports": get_traffic_reports.handle,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        find_journey.get_tool(),
        find_places.get_tool(),
        find_nearby_places.get_tool(),
        get_departures.get_tool(),
        get_arrivals.get_tool(),
        get_coverage.get_tool(),
        get_line_reports.get_tool(),
        get_traffic_reports.get_tool(),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls."""
    try:
        # Get handler from mapping
        handler = TOOL_HANDLERS.get(name)
        
        if handler:
            return await handler(navitia_client, arguments)
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unknown tool: {name}",
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error calling tool '{name}' with arguments {arguments}: {str(e)}",
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
