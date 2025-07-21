"""
Shared format handling utilities for map-locations packages.

This module provides functions for loading and saving location data
in various formats, with a focus on YAML as the primary format.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, cast

import yaml

from .models import Location, LocationList


def load_locations_from_yaml(yaml_path: str) -> LocationList:
    """
    Load locations from a YAML file with the expected structure.

    Args:
        yaml_path: Path to the YAML file containing location data

    Returns:
        List of location dictionaries with standardized structure

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is malformed

    Example:
        >>> from map_locations.common import load_locations_from_yaml
        >>> locations = load_locations_from_yaml("my_locations.yaml")
        >>> print(f"Loaded {len(locations)} locations")
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"YAML file not found: {yaml_path}")

    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            data = cast(Dict[str, Any], yaml.safe_load(f))
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file {yaml_path}: {e}")

    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a dictionary, got {type(data)}")

    locations = data.get("locations", [])
    if not isinstance(locations, list):
        raise ValueError("YAML file must contain a 'locations' key with a list value")

    return cast(LocationList, locations)


def save_locations_to_yaml(locations: LocationList, yaml_path: str) -> None:
    """
    Save locations to a YAML file with proper formatting.

    Args:
        locations: List of location dictionaries
        yaml_path: Path to save the YAML file

    Raises:
        OSError: If the file cannot be written

    Example:
        >>> from map_locations.common import save_locations_to_yaml
        >>> save_locations_to_yaml(locations, "output.yaml")
    """
    # Create directory if needed
    output_dir = os.path.dirname(yaml_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    data = {"locations": locations}

    try:
        with open(yaml_path, "w", encoding="utf-8") as f:
            yaml.dump(
                data, f, default_flow_style=False, allow_unicode=True, sort_keys=False, indent=2
            )
        print(f"📄 YAML saved to: {Path(yaml_path).resolve()}")
    except OSError as e:
        raise OSError(f"Error writing YAML file {yaml_path}: {e}")


def validate_location(location: Dict[str, Any]) -> Location:
    """
    Validate and clean a location dictionary.

    Args:
        location: Raw location dictionary

    Returns:
        Validated Location object

    Raises:
        ValueError: If required fields are missing or invalid
    """
    # Check required fields
    required_fields = ["name", "type", "latitude", "longitude"]
    for field in required_fields:
        if field not in location:
            raise ValueError(f"Missing required field: {field}")

    # Validate coordinate ranges
    lat = location["latitude"]
    lon = location["longitude"]
    if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90.")
    if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180.")

    # Ensure tags is a list
    if "tags" in location and not isinstance(location["tags"], list):
        location["tags"] = []

    return cast(Location, location)


def validate_locations(locations: List[Dict[str, Any]]) -> LocationList:
    """
    Validate a list of location dictionaries.

    Args:
        locations: List of raw location dictionaries

    Returns:
        List of validated Location objects

    Raises:
        ValueError: If any location is invalid
    """
    validated_locations = []
    for i, location in enumerate(locations):
        try:
            validated_locations.append(validate_location(location))
        except ValueError as e:
            raise ValueError(f"Error in location {i}: {e}")

    return validated_locations
