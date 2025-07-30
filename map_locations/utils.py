"""
Utility functions for the Map Locations library.

This module contains helper functions for creating sample data and other utilities.
"""

from .common import LocationList


def create_sample_locations() -> LocationList:
    """
    Create sample location data for testing and examples.

    Returns:
        List of sample location dictionaries

    Example:
        >>> sample_locations = create_sample_locations()
        >>> show_locations_grouped(sample_locations, "sample_map.html")
    """
    return [
        {
            "name": "Eiffel Tower",
            "type": "landmark",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "tags": ["historic", "iconic"],
            "neighborhood": "7th arrondissement",
            "date_added": "2024-01-15",
        },
        {
            "name": "Louvre Museum",
            "type": "museum",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "tags": ["art", "historic"],
            "neighborhood": "1st arrondissement",
            "date_added": "2024-01-15",
        },
        {
            "name": "Notre-Dame Cathedral",
            "type": "church",
            "latitude": 48.8530,
            "longitude": 2.3499,
            "tags": ["historic", "architecture"],
            "neighborhood": "4th arrondissement",
            "date_added": "2024-01-15",
        },
    ]
