"""
Color category management and location type classification.

This module handles color coding, category mapping, and type classification
for location data in the Map Locations library.
"""

from typing import Any, Dict, List

# Import common models
from .common import LocationList

# Color category mapping for filtering
COLOR_CATEGORIES = {
    "Food / Drink": {
        "color": "red",
        "hex_color": "#ff0000",
        "types": ["restaurant", "cafe", "bar", "pub"],
        "emoji": "🍽️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #ff0000; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Culture + Arts": {
        "color": "lightblue",
        "hex_color": "#87ceeb",
        "types": [
            "museum",
            "gallery",
            "art gallery",
            "theater",
            "cinema",
            "exhibition",
            "studio tour",
        ],
        "emoji": "🎭",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #87ceeb; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Nature + Outdoors": {
        "color": "green",
        "hex_color": "#00ff00",
        "types": ["park", "garden", "botanical garden", "cemetery"],
        "emoji": "🌳",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #00ff00; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Covered Passages + Arcades": {
        "color": "cadetblue",
        "hex_color": "#5f9ea0",
        "types": ["passage", "covered passage", "passage couvert", "arcade", "gallery"],
        "emoji": "🏛️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #5f9ea0; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Shopping + Commerce": {
        "color": "blue",
        "hex_color": "#0000ff",
        "types": ["shopping", "store", "market", "shopping center", "shopping street"],
        "emoji": "🛍️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #0000ff; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Accommodation": {
        "color": "lightgray",
        "hex_color": "#d3d3d3",
        "types": ["hotel", "accommodation", "apartment"],
        "emoji": "🏨",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #d3d3d3; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Transport": {
        "color": "gray",
        "hex_color": "#808080",
        "types": ["transport", "station", "metro station"],
        "emoji": "🚇",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #808080; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Landmarks / Monuments": {
        "color": "orange",
        "hex_color": "#ffa500",
        "types": [
            "landmark",
            "monument",
            "church",
            "temple",
            "basilica",
            "palace",
            "bridge",
        ],
        "emoji": "🏛️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #ffa500; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Entertainment / Experiences": {
        "color": "purple",
        "hex_color": "#800080",
        "types": ["entertainment", "theme park", "amusement park", "experience"],
        "emoji": "🎢",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #800080; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Neighborhoods / Areas": {
        "color": "darkred",
        "hex_color": "#8b0000",
        "types": ["neighborhood", "district", "theater district"],
        "emoji": "🏘️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #8b0000; border-radius: 2px; margin-left: 4px;"></span>',
    },
    "Streets / Urban": {
        "color": "darkgray",
        "hex_color": "#404040",
        "types": ["street"],
        "emoji": "🛣️",
        "square": '<span style="display: inline-block; width: 12px; height: 12px; background-color: #404040; border-radius: 2px; margin-left: 4px;"></span>',
    },
}

# Derive FOLIUM_TO_HEX_COLORS from COLOR_CATEGORIES to eliminate duplication
FOLIUM_TO_HEX_COLORS = {
    category_info["color"]: category_info["hex_color"]
    for category_info in COLOR_CATEGORIES.values()
}


def get_color_square_html(color: str, size: int = 12) -> str:
    """
    Generate HTML for a colored square.

    Args:
        color (str): Color name or hex value
        size (int): Size of the square in pixels

    Returns:
        str: HTML for the colored square
    """
    # Use the centralized color mapping
    hex_color = FOLIUM_TO_HEX_COLORS.get(color, color)
    return f'<div style="display: inline-block; width: {size}px; height: {size}px; background-color: {hex_color}; border: 1px solid #ccc; border-radius: 2px; margin-right: 6px;"></div>'


def get_location_category(loc_type: str) -> str:
    """
    Get the color category for a location type.

    Args:
        loc_type (str): The location type

    Returns:
        str: The category name or "Other" if not found
    """
    loc_type_lower = loc_type.lower()
    for category, info in COLOR_CATEGORIES.items():
        if loc_type_lower in [t.lower() for t in info["types"]]:
            return category
    return "Other"


def get_category_types(category: str) -> List[str]:
    """
    Get all types that belong to a specific category.

    Args:
        category (str): The category name

    Returns:
        List[str]: List of types in the category
    """
    types = COLOR_CATEGORIES.get(category, {}).get("types", [])
    return list(types)  # Ensure we return a list, not a sequence


def get_type_color(loc_type: str, format: str = "folium") -> str:
    """
    Get the appropriate color for a location type.

    Args:
        loc_type (str): The location type
        format (str): Color format - "folium" for folium maps, "kml" for KML export

    Returns:
        str: The color value in the specified format
    """
    # Get category for the location type
    category = get_location_category(loc_type)

    if category in COLOR_CATEGORIES:
        if format == "kml":
            kml_color: str = str(get_kml_color(loc_type))
            return kml_color
        else:  # folium format
            folium_color: str = str(COLOR_CATEGORIES[category]["color"])
            return folium_color

    # Default colors for unknown types
    if format == "kml":
        return "ff808080"  # Gray in KML format
    else:
        return "gray"  # Gray in folium format


def get_available_categories(locations: LocationList) -> List[str]:
    """
    Get a list of all available categories from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique categories that have locations
    """
    categories = set()
    for loc in locations:
        category = get_location_category(loc.get("type", ""))
        if category != "Other":
            categories.add(category)
    return sorted(list(categories))


def filter_locations_by_category(
    locations: LocationList, categories: List[str]
) -> LocationList:
    """
    Filter locations by their color category.

    Args:
        locations: List of location dictionaries
        categories: List of categories to include

    Returns:
        Filtered list of locations
    """
    filtered_locations = []
    for loc in locations:
        loc_category = get_location_category(loc.get("type", ""))
        if loc_category in categories:
            filtered_locations.append(loc)
    return filtered_locations


def hex_to_kml_color(hex_color: str) -> str:
    """
    Convert hex color to KML format (AABBGGRR).

    Args:
        hex_color (str): Hex color in format "#RRGGBB"

    Returns:
        str: KML color in AABBGGRR format
    """
    # Remove # if present
    hex_color = hex_color.lstrip("#")

    # Parse RGB components
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    # KML format is AABBGGRR (Alpha, Blue, Green, Red)
    # Alpha = 255 (fully opaque)
    # Note: KML uses little-endian byte order
    return f"ff{b:02x}{g:02x}{r:02x}"


def get_kml_color(loc_type: str) -> str:
    """
    Get KML color for a location type.

    Args:
        loc_type (str): The location type

    Returns:
        str: KML color in AABBGGRR format
    """
    # Get category for the location type
    category = get_location_category(loc_type)

    if category in COLOR_CATEGORIES:
        hex_color = str(COLOR_CATEGORIES[category]["hex_color"])
        return hex_to_kml_color(hex_color)

    # Default gray for unknown types
    return "ff808080"
