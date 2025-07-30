"""
Map Locations - A Python library for mapping locations with interactive filtering and
visualization capabilities.

This library provides tools for creating interactive maps, filtering locations,
and exporting data in various formats including KML, GeoJSON, and HTML.
"""

__version__ = "0.2.1"
__author__ = "Lavi Shpigelman"
__email__ = "shpigi+map_locations@gmail.com"

# Import category functions
from .categories import (
    COLOR_CATEGORIES,
    filter_locations_by_category,
    get_available_categories,
    get_location_category,
    get_type_color,
)

# Import main functions for easy access
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
    show_locations_with_advanced_filtering,
    show_locations_with_filtering,
    show_locations_with_google_maps,
    validate_location_data,
)

__all__ = [
    "Location",
    "load_locations_from_yaml",
    "show_locations_grouped",
    "show_locations_with_filtering",
    "show_locations_with_advanced_filtering",
    "export_to_json",
    "export_to_csv",
    "export_to_geojson",
    "export_to_kml",
    "export_to_all_formats",
    "get_available_types",
    "get_available_tags",
    "get_available_neighborhoods",
    "get_available_categories",
    "filter_locations_by_type",
    "filter_locations_by_tags",
    "filter_locations_by_neighborhood",
    "filter_locations_by_category",
    "get_location_summary",
    "validate_location_data",
    "create_sample_locations",
    "show_locations_with_google_maps",
    "get_location_category",
    "get_type_color",
    "COLOR_CATEGORIES",
]


def get_version() -> str:
    """Get the current version of the package."""
    return __version__
