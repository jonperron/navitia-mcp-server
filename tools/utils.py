"""Utility functions for the Navitia MCP server."""

from datetime import datetime


def parse_iso_datetime(datetime_str: str) -> datetime:
    """
    Parse an ISO format datetime string with validation.
    
    Args:
        datetime_str: Datetime string in ISO format (e.g., '2024-06-01T08:00:00')
        
    Returns:
        Parsed datetime object
        
    Raises:
        ValueError: If datetime string is not in valid ISO format
    """
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError as e:
        raise ValueError(
            f"Invalid datetime format: '{datetime_str}'. "
            "Expected ISO format (e.g., '2024-06-01T08:00:00' or '2024-06-01T08:00:00+02:00'). "
            f"Error: {str(e)}"
        )
