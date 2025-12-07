"""Formatters for Navitia API responses."""

from typing import Any


def format_datetime(dt: Any) -> str | None:
    """Format a datetime object to ISO format string.
    
    Args:
        dt: Datetime object to format
        
    Returns:
        ISO format string or None if dt is None
    """
    return dt.isoformat() if dt else None


def format_journey(journey: Any) -> dict:
    """Format a journey object for display."""
    return {
        "duration": journey.duration,
        "nb_transfers": journey.nb_transfers,
        "departure_time": format_datetime(journey.departure_date_time),
        "arrival_time": format_datetime(journey.arrival_date_time),
        "type": journey.type,
        "sections": (
            [
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
                    "display_informations": (
                        {
                            "direction": (
                                section.display_informations.direction
                                if section.display_informations
                                else None
                            ),
                            "code": (
                                section.display_informations.code
                                if section.display_informations
                                else None
                            ),
                            "network": (
                                section.display_informations.network
                                if section.display_informations
                                else None
                            ),
                            "color": (
                                section.display_informations.color
                                if section.display_informations
                                else None
                            ),
                        }
                        if section.display_informations
                        else None
                    ),
                }
                for section in journey.sections
            ]
            if journey.sections
            else []
        ),
    }


def format_place(place: Any) -> dict:
    """Format a place object for display."""
    return {
        "id": place.id,
        "name": place.name,
        "quality": place.quality if hasattr(place, "quality") else None,
        "embedded_type": (
            place.embedded_type if hasattr(place, "embedded_type") else None
        ),
        "administrative_regions": (
            [
                {"name": region.name, "level": region.level}
                for region in place.administrative_regions
            ]
            if hasattr(place, "administrative_regions") and place.administrative_regions
            else []
        ),
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
            "direction": (
                departure.route.direction.name
                if departure.route and departure.route.direction
                else None
            ),
        },
        "stop_date_time": {
            "departure_date_time": format_datetime(
                departure.stop_date_time.departure_date_time
                if departure.stop_date_time
                else None
            ),
            "base_departure_date_time": format_datetime(
                departure.stop_date_time.base_departure_date_time
                if departure.stop_date_time
                else None
            ),
        },
        "display_informations": (
            {
                "direction": (
                    departure.display_informations.direction
                    if departure.display_informations
                    else None
                ),
                "code": (
                    departure.display_informations.code
                    if departure.display_informations
                    else None
                ),
                "network": (
                    departure.display_informations.network
                    if departure.display_informations
                    else None
                ),
                "color": (
                    departure.display_informations.color
                    if departure.display_informations
                    else None
                ),
            }
            if departure.display_informations
            else None
        ),
    }
