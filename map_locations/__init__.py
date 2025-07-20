"""
Map Locations - A Python library for mapping locations with interactive filtering and
visualization.

This package provides tools for loading location data from YAML files,
creating interactive maps with Folium, and exporting to various formats
including JSON, CSV, GeoJSON, and KML.
"""

__version__ = "0.1.0"
__author__ = "Lavi Shpigelman"
__email__ = "shpigi+map_locations@gmail.com"

from .core import (
    Location,
    create_sample_locations,
    export_to_all_formats,
    export_to_csv,
    export_to_geojson,
    export_to_json,
    export_to_kml,
    filter_locations_by_neighborhood,
    filter_locations_by_tags,
    filter_locations_by_type,
    get_available_neighborhoods,
    get_available_tags,
    get_available_types,
    get_location_summary,
    load_locations_from_yaml,
    show_locations_grouped,
    show_locations_with_filtering,
    show_locations_with_google_maps,
    validate_location_data,
)

__all__ = [
    "Location",
    "load_locations_from_yaml",
    "export_to_json",
    "export_to_csv",
    "export_to_geojson",
    "export_to_kml",
    "export_to_all_formats",
    "show_locations_grouped",
    "show_locations_with_filtering",
    "show_locations_with_google_maps",
    "get_available_types",
    "get_available_tags",
    "get_available_neighborhoods",
    "filter_locations_by_type",
    "filter_locations_by_tags",
    "filter_locations_by_neighborhood",
    "get_location_summary",
    "validate_location_data",
    "create_sample_locations",
]
