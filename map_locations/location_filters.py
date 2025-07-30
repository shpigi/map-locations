"""
Location analysis and filtering functions.

This module provides functions for analyzing location data, filtering by various
criteria, and validating location information.
"""

from collections import Counter
from typing import Any, Dict, List

from .categories import get_available_categories, get_location_category
from .common import LocationList


def get_available_types(locations: LocationList) -> List[str]:
    """
    Get a list of all available location types from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique location types

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> types = get_available_types(locations)
        >>> print(f"Available types: {types}")
    """
    return sorted(
        list(set(loc.get("type", "") for loc in locations if loc.get("type")))
    )


def get_available_tags(locations: LocationList) -> List[str]:
    """
    Get a list of all available tags from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique tags across all locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> tags = get_available_tags(locations)
        >>> print(f"Available tags: {tags}")
    """
    all_tags = set()
    for loc in locations:
        if "tags" in loc and isinstance(loc["tags"], list):
            all_tags.update(loc["tags"])
    return sorted(list(all_tags))


def get_available_neighborhoods(locations: LocationList) -> List[str]:
    """
    Get a list of all available neighborhoods from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique neighborhoods

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> neighborhoods = get_available_neighborhoods(locations)
        >>> print(f"Available neighborhoods: {neighborhoods}")
    """
    return sorted(
        list(
            set(
                loc.get("neighborhood", "")
                for loc in locations
                if loc.get("neighborhood")
            )
        )
    )


def filter_locations_by_type(
    locations: LocationList, location_types: List[str]
) -> LocationList:
    """
    Filter locations by their type.

    Args:
        locations: List of location dictionaries
        location_types: List of types to include

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> restaurants = filter_locations_by_type(locations, ["restaurant", "cafe"])
        >>> print(f"Found {len(restaurants)} food locations")
    """
    return [loc for loc in locations if loc.get("type") in location_types]


def filter_locations_by_tags(locations: LocationList, tags: List[str]) -> LocationList:
    """
    Filter locations by tags (locations must have at least one of the specified tags).

    Args:
        locations: List of location dictionaries
        tags: List of tags to filter by

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> historic_sites = filter_locations_by_tags(locations, ["historic"])
        >>> print(f"Found {len(historic_sites)} historic locations")
    """
    return [
        loc
        for loc in locations
        if "tags" in loc
        and isinstance(loc["tags"], list)
        and any(tag in loc["tags"] for tag in tags)
    ]


def filter_locations_by_neighborhood(
    locations: LocationList, neighborhoods: List[str]
) -> LocationList:
    """
    Filter locations by neighborhood.

    Args:
        locations: List of location dictionaries
        neighborhoods: List of neighborhoods to include

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> downtown = filter_locations_by_neighborhood(locations, ["downtown"])
        >>> print(f"Found {len(downtown)} downtown locations")
    """
    return [loc for loc in locations if loc.get("neighborhood") in neighborhoods]


def get_location_summary(locations: LocationList) -> Dict[str, Any]:
    """
    Get a summary of location data including counts and available options.

    Args:
        locations: List of location dictionaries

    Returns:
        Dictionary with summary information

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> summary = get_location_summary(locations)
        >>> print(f"Total locations: {summary['total_count']}")
        >>> print(f"Types: {summary['types']}")
    """
    # Get category counts
    category_counts: Counter[str] = Counter()
    for loc in locations:
        category = get_location_category(loc.get("type", ""))
        category_counts[category] += 1

    return {
        "total_count": len(locations),
        "types": get_available_types(locations),
        "categories": get_available_categories(locations),
        "tags": get_available_tags(locations),
        "neighborhoods": get_available_neighborhoods(locations),
        "type_counts": dict(Counter(loc.get("type", "") for loc in locations)),
        "category_counts": dict(category_counts),
        "neighborhood_counts": dict(
            Counter(loc.get("neighborhood", "") for loc in locations)
        ),
    }


def validate_location_data(locations: LocationList) -> Dict[str, List[str]]:
    """
    Validate location data and return any issues found.

    Args:
        locations: List of location dictionaries

    Returns:
        Dictionary with validation issues by category

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> issues = validate_location_data(locations)
        >>> if issues['missing_required']:
        >>>     print(f"Missing required fields: {issues['missing_required']}")
    """
    issues: Dict[str, List[str]] = {
        "missing_required": [],
        "invalid_coordinates": [],
        "invalid_dates": [],
    }

    for i, loc in enumerate(locations):
        # Check required fields
        if not loc.get("name"):
            issues["missing_required"].append(f"Location {i + 1}: missing name")
        if not loc.get("type"):
            issues["missing_required"].append(f"Location {i + 1}: missing type")
        if loc.get("latitude") is None:
            issues["missing_required"].append(f"Location {i + 1}: missing latitude")
        if loc.get("longitude") is None:
            issues["missing_required"].append(f"Location {i + 1}: missing longitude")

        # Check coordinate validity
        lat = loc.get("latitude")
        lon = loc.get("longitude")
        if lat is not None and lon is not None:
            if not (-90 <= lat <= 90):
                issues["invalid_coordinates"].append(
                    f"Location {i + 1}: invalid latitude {lat}"
                )
            if not (-180 <= lon <= 180):
                issues["invalid_coordinates"].append(
                    f"Location {i + 1}: invalid longitude {lon}"
                )

    return issues
