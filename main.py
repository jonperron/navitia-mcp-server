#!/usr/bin/env python3
"""
Navitia MCP Server

A Model Context Protocol server that provides access to real-time transit information
through the Navitia API.
"""

import os
import json
from datetime import datetime
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from navitia_client.client.navitia_client import NavitiaClient
from navitia_client.entities.request.journey import JourneyRequest
from navitia_client.entities.request.places_nearby import PlacesNearbyRequest
from navitia_client.entities.request.departure import DepartureRequest
from navitia_client.entities.request.arrival import ArrivalRequest
from navitia_client.entities.request.line_report import LineReportRequest
from navitia_client.entities.request.traffic_report import TrafficReportRequest


# Initialize Navitia client
NAVITIA_TOKEN = os.getenv("NAVITIA_API_TOKEN")
if not NAVITIA_TOKEN:
    raise ValueError("NAVITIA_API_TOKEN environment variable must be set")

navitia_client = NavitiaClient(auth_token=NAVITIA_TOKEN)

# Initialize MCP server
server = Server("navitia-mcp-server")


def format_journey(journey: Any) -> dict:
    """Format a journey object for display."""
    return {
        "duration": journey.duration,
        "nb_transfers": journey.nb_transfers,
        "departure_time": journey.departure_date_time.isoformat() if journey.departure_date_time else None,
        "arrival_time": journey.arrival_date_time.isoformat() if journey.arrival_date_time else None,
        "type": journey.type,
        "sections": [
            {
                "type": section.type,
                "mode": section.mode if hasattr(section, "mode") else None,
                "duration": section.duration,
                "from": {
                    "name": section.from_.name if section.from_ else None,
                    "id": section.from_.id if section.from_ else None,
                },
                "to": {
                    "name": section.to.name if section.to else None,
                    "id": section.to.id if section.to else None,
                },
                "display_informations": {
                    "direction": section.display_informations.direction if section.display_informations else None,
                    "code": section.display_informations.code if section.display_informations else None,
                    "network": section.display_informations.network if section.display_informations else None,
                    "color": section.display_informations.color if section.display_informations else None,
                } if section.display_informations else None,
            }
            for section in journey.sections
        ] if journey.sections else [],
    }


def format_place(place: Any) -> dict:
    """Format a place object for display."""
    return {
        "id": place.id,
        "name": place.name,
        "quality": place.quality if hasattr(place, "quality") else None,
        "embedded_type": place.embedded_type if hasattr(place, "embedded_type") else None,
        "administrative_regions": [
            {"name": region.name, "level": region.level}
            for region in place.administrative_regions
        ] if hasattr(place, "administrative_regions") and place.administrative_regions else [],
    }


def format_departure(departure: Any) -> dict:
    """Format a departure object for display."""
    return {
        "stop_point": {
            "name": departure.stop_point.name if departure.stop_point else None,
            "id": departure.stop_point.id if departure.stop_point else None,
        },
        "route": {
            "name": departure.route.name if departure.route else None,
            "direction": departure.route.direction.name if departure.route and departure.route.direction else None,
        },
        "stop_date_time": {
            "departure_date_time": departure.stop_date_time.departure_date_time.isoformat() if departure.stop_date_time and departure.stop_date_time.departure_date_time else None,
            "base_departure_date_time": departure.stop_date_time.base_departure_date_time.isoformat() if departure.stop_date_time and departure.stop_date_time.base_departure_date_time else None,
        },
        "display_informations": {
            "direction": departure.display_informations.direction if departure.display_informations else None,
            "code": departure.display_informations.code if departure.display_informations else None,
            "network": departure.display_informations.network if departure.display_informations else None,
            "color": departure.display_informations.color if departure.display_informations else None,
        } if departure.display_informations else None,
    }


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
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
        ),
        Tool(
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
                "required": ["query"],
            },
        ),
        Tool(
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
        ),
        Tool(
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
                "required": ["stop_id"],
            },
        ),
        Tool(
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
                "required": ["stop_id"],
            },
        ),
        Tool(
            name="get_coverage",
            description="Get list of regions covered by the Navitia API. Use this to discover available region IDs.",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
        Tool(
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
        ),
        Tool(
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
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """Handle tool calls."""
    
    try:
        if name == "find_journey":
            # Parse datetime if provided
            dt = None
            if "datetime" in arguments:
                dt = datetime.fromisoformat(arguments["datetime"])
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
        
        elif name == "find_places":
            # Use places API
            places = navitia_client.places.list_objects(
                q=arguments["query"],
                region_id=arguments.get("region_id"),
                type=arguments.get("type"),
            )
            
            results = [format_place(p) for p in places]
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]
        
        elif name == "find_nearby_places":
            # Create request
            request = PlacesNearbyRequest(
                distance=arguments.get("distance", 500),
                type=tuple(arguments.get("type", ["stop_area", "stop_point"])),
            )
            
            location = arguments["location"]
            
            # Try to parse as coordinates
            if ";" in location:
                lon, lat = location.split(";")
                places, pagination = navitia_client.places_nearby.list_objects_by_object_coordinates_only(
                    lon=float(lon),
                    lat=float(lat),
                    request=request,
                )
            else:
                # Use as resource path
                region_id = arguments.get("region_id", "")
                if not region_id:
                    return [TextContent(type="text", text="Error: region_id required when using stop IDs")]
                
                places, pagination = navitia_client.places_nearby.list_objects_by_region_id_and_path(
                    region_id=region_id,
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
        
        elif name == "get_departures":
            # Parse datetime if provided
            dt = None
            if "from_datetime" in arguments:
                dt = datetime.fromisoformat(arguments["from_datetime"])
            
            # Create request
            request = DepartureRequest(
                from_datetime=dt.isoformat() if dt else None,
                duration=arguments.get("duration", 3600),
            )
            
            stop_id = arguments["stop_id"]
            
            if "region_id" in arguments:
                departures = navitia_client.departures.list_objects_by_region_id_and_path(
                    region_id=arguments["region_id"],
                    resource_path=stop_id,
                    request=request,
                )
            else:
                # Try to extract region from stop_id
                return [TextContent(type="text", text="Error: region_id required")]
            
            results = [format_departure(d) for d in departures]
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]
        
        elif name == "get_arrivals":
            # Parse datetime if provided
            dt = None
            if "from_datetime" in arguments:
                dt = datetime.fromisoformat(arguments["from_datetime"])
            
            # Create request
            request = ArrivalRequest(
                from_datetime=dt.isoformat() if dt else None,
                duration=arguments.get("duration", 3600),
            )
            
            stop_id = arguments["stop_id"]
            
            if "region_id" in arguments:
                arrivals = navitia_client.arrivals.list_objects_by_id_and_path(
                    region_id=arguments["region_id"],
                    resource_path=stop_id,
                    request=request,
                )
            else:
                return [TextContent(type="text", text="Error: region_id required")]
            
            results = [format_departure(a) for a in arrivals]  # Same format as departures
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]
        
        elif name == "get_coverage":
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
        
        elif name == "get_line_reports":
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
                    "pt_objects": [
                        {
                            "id": obj.id,
                            "name": obj.name if hasattr(obj, "name") else None,
                        }
                        for obj in report.pt_objects
                    ] if report.pt_objects else [],
                }
                for report in reports
            ]
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]
        
        elif name == "get_traffic_reports":
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
                    "lines": [
                        {
                            "id": line.id,
                            "name": line.name if hasattr(line, "name") else None,
                        }
                        for line in report.lines
                    ] if report.lines else [],
                }
                for report in reports
            ]
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2),
                )
            ]
        
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
                text=f"Error: {str(e)}",
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
