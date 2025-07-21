"""
Common utilities and data models for map-locations packages.

This package contains common data models and utilities used by both
the mapping tools (map_locations) and AI agent (map_locations_ai) packages.
"""

from .formats import load_locations_from_yaml, save_locations_to_yaml
from .models import Location, LocationList

__version__ = "0.1.0"
__all__ = ["Location", "LocationList", "load_locations_from_yaml", "save_locations_to_yaml"]
