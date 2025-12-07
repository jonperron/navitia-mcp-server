# Navitia MCP Server

A Model Context Protocol (MCP) server that provides AI agents with access to real-time transit information through the Navitia API.

## Features

This MCP server exposes the following tools:

### Journey Planning

- **find_journey**: Find transit routes between two locations with real-time data

### Transit Information

- **find_places**: Search for transit stops, addresses, and points of interest
- **find_nearby_places**: Find transit options near a location
- **get_departures**: Get real-time departure information from a stop
- **get_arrivals**: Get real-time arrival information at a stop

### Service Information

- **get_coverage**: Get list of available regions/coverage areas
- **get_line_reports**: Check service status and disruptions for transit lines
- **get_traffic_reports**: Get traffic reports and disruptions for a region

## Prerequisites

- Python >= 3.13
- A Navitia API token from [navitia.io](https://navitia.io/tarifs/)

## Installation

```bash
pip install -e .
```

## Configuration

Set your Navitia API token as an environment variable:

```bash
export NAVITIA_API_TOKEN="your_token_here"
```

## Usage

### Running the Server

```bash
python server.py
```

Or using the MCP CLI:

```bash
mcp run server.py
```

### Using with Claude Desktop

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "navitia": {
      "command": "python",
      "args": ["/path/to/navitia-mcp-server/server.py"],
      "env": {
        "NAVITIA_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

## Example Queries

Once connected, you can ask Claude:

- "Find me a route from Gare de Lyon to Charles de Gaulle Airport tomorrow at 9am"
- "What are the next departures from Châtelet station?"
- "Are there any disruptions on Line 1 in Paris?"
- "Find transit stops near the Eiffel Tower"
- "What regions are covered by the Navitia API?"

## Tool Reference

### find_journey

Find a transit journey between two locations.

**Parameters:**

- `from_location` (str, required): Starting point (stop ID, address, or coordinates)
- `to_location` (str, required): Destination (stop ID, address, or coordinates)
- `datetime` (str, optional): Departure/arrival datetime in ISO format
- `datetime_represents` (str, optional): "departure" or "arrival" (default: "departure")
- `region_id` (str, optional): Specific region to search in
- `count` (int, optional): Number of journeys to return (default: 5)

**Returns:** List of journey options with legs, durations, and transit information

### find_places

Search for places (stops, addresses, POIs).

**Parameters:**

- `query` (str, required): Search query
- `region_id` (str, required): Limit search to specific region
- `type` (list[str], optional): Types to search: "stop_area", "address", "poi", etc.

**Returns:** List of matching places with details

### find_nearby_places

Find transit options near a location.

**Parameters:**

- `location` (str, required): Location (stop ID, address, or coordinates)
- `region_id` (str, required): Region to search in
- `distance` (int, optional): Search radius in meters (default: 500)
- `type` (list[str], optional): Types to find (default: ["stop_area", "stop_point"])

**Returns:** Nearby places with distances

### get_departures

Get upcoming departures from a stop.

**Parameters:**

- `stop_id` (str, required): Stop area or stop point ID
- `region_id` (str, required): Region ID
- `from_datetime` (str, optional): Start datetime for departures
- `duration` (int, optional): Time window in seconds (default: 3600)

**Returns:** List of upcoming departures with real-time information

### get_arrivals

Get upcoming arrivals at a stop.

**Parameters:**

- `stop_id` (str, required): Stop area or stop point ID
- `region_id` (str, required): Region ID
- `from_datetime` (str, optional): Start datetime for arrivals
- `duration` (int, optional): Time window in seconds (default: 3600)

**Returns:** List of upcoming arrivals with real-time information

### get_coverage

Get list of regions covered by the API.

**Returns:** List of available regions with their IDs and geographic coverage

### get_line_reports

Get service status for transit lines.

**Parameters:**

- `region_id` (str, required): Region ID
- `resource_path` (str, optional): Path to specific line (e.g., 'lines/line:RAT:M1')

**Returns:** Line status and disruption information

### get_traffic_reports

Get traffic reports and disruptions.

**Parameters:**

- `region_id` (str, required): Region ID

**Returns:** Current traffic reports and service disruptions

## Development

### Running Tests

```bash
pytest
```

### Project Structure

```
navitia-mcp-server/
├── server.py           # Main MCP server implementation
├── pyproject.toml      # Project configuration
├── tools/              # MCP tools
└── tests/              # Test suite
    └── test_server.py
```

## License

MIT License - Same as python-navitia-client

## Links

- [Navitia API Documentation](https://doc.navitia.io)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [python-navitia-client](https://github.com/jonperron/python-navitia-client)
