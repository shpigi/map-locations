"""
Map Locations - A Python library for mapping locations with interactive filtering and visualization.

This package provides tools for loading location data from YAML files,
creating interactive maps with Folium, and exporting to various formats
including JSON, CSV, GeoJSON, and KML.
"""

__version__ = "0.1.0"
__author__ = "Lavi Shpigelman"
__email__ = "shpigi+map_locations@gmail.com"

from .core import (
    load_locations_from_yaml,
    export_to_json,
    export_to_csv,
    export_to_geojson,
    export_to_kml,
    export_to_all_formats,
    show_locations_grouped,
)

__all__ = [
    "load_locations_from_yaml",
    "export_to_json",
    "export_to_csv",
    "export_to_geojson",
    "export_to_kml",
    "export_to_all_formats",
    "show_locations_grouped",
] 