# AI Agent Guide

Complete guide for AI agents using the Map Locations package.

## Table of Contents

- [Overview](#overview)
- [Core Data Structure](#core-data-structure)
- [Quick Start for AI Agents](#quick-start-for-ai-agents)
- [Available Functions](#available-functions)
- [Common Workflows](#common-workflows)
- [Data Validation](#data-validation)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

This package is designed to be AI-agent friendly with comprehensive type hints, clear function signatures, and utility functions for common operations.

## Core Data Structure

```python
from map_locations import Location

# Location is a TypedDict with the following structure:
Location = {
    "name": str,           # Required: Location name
    "type": str,           # Required: Location type/category
    "latitude": float,      # Required: Latitude coordinate
    "longitude": float,     # Required: Longitude coordinate
    "tags": List[str],      # Optional: List of tags for filtering
    "neighborhood": str,    # Optional: Neighborhood or area name
    "date_added": str,      # Optional: Date when added (YYYY-MM-DD)
    "date_of_visit": str,   # Optional: Date of visit (YYYY-MM-DD)
}
```

## Quick Start for AI Agents

```python
from map_locations import (
    load_locations_from_yaml,
    create_sample_locations,
    get_location_summary,
    filter_locations_by_type,
    validate_location_data,
    show_locations_grouped,
    export_to_all_formats,
)

# Load existing data or create sample data
locations = load_locations_from_yaml("my_locations.yaml")
# OR
locations = create_sample_locations()

# Get summary of available data
summary = get_location_summary(locations)
print(f"Total locations: {summary['total_count']}")
print(f"Available types: {summary['types']}")
print(f"Available tags: {summary['tags']}")

# Validate data for issues
issues = validate_location_data(locations)
if issues['missing_required']:
    print(f"Data issues found: {issues}")

# Filter and visualize
restaurants = filter_locations_by_type(locations, ["restaurant", "cafe"])
show_locations_grouped(restaurants, "restaurants_map.html")

# Export to multiple formats
export_to_all_formats(locations, "exports/my_locations")
```

## Available Functions

### Data Loading and Validation
- `load_locations_from_yaml(yaml_path: str) -> List[Location]`
- `create_sample_locations() -> List[Location]`
- `validate_location_data(locations: List[Location]) -> Dict[str, List[str]]`

### Data Analysis
- `get_location_summary(locations: List[Location]) -> Dict[str, Any]`
- `get_available_types(locations: List[Location]) -> List[str]`
- `get_available_tags(locations: List[Location]) -> List[str]`
- `get_available_neighborhoods(locations: List[Location]) -> List[str]`

### Filtering
- `filter_locations_by_type(locations: List[Location], types: List[str]) -> List[Location]`
- `filter_locations_by_tags(locations: List[Location], tags: List[str]) -> List[Location]`
- `filter_locations_by_neighborhood(locations: List[Location], neighborhoods: List[str]) -> List[Location]`

### Visualization
- `show_locations_grouped(locations: List[Location], group_by: str = "type", map_filename: str = "map.html")`
- `show_locations_with_filtering(locations: List[Location], map_filename: str = "map.html")`
- `show_locations_with_google_maps(locations: List[Location], map_filename: str = "map.html")`

### Export
- `export_to_json(locations: List[Location], output_path: str)`
- `export_to_csv(locations: List[Location], output_path: str)`
- `export_to_geojson(locations: List[Location], output_path: str)`
- `export_to_kml(locations: List[Location], output_path: str)`
- `export_to_all_formats(locations: List[Location], base_path: str)`

## Common Workflows

### 1. Data Exploration

```python
from map_locations import load_locations_from_yaml, get_location_summary

locations = load_locations_from_yaml("data.yaml")
summary = get_location_summary(locations)
print(f"Dataset contains {summary['total_count']} locations")
print(f"Types: {summary['types']}")
print(f"Top types: {dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:5])}")
```

### 2. Data Validation

```python
from map_locations import validate_location_data

issues = validate_location_data(locations)
if any(issues.values()):
    print("Data validation issues found:")
    for category, problems in issues.items():
        if problems:
            print(f"  {category}: {problems}")
else:
    print("✅ Data validation passed")
```

### 3. Filtered Analysis

```python
from map_locations import filter_locations_by_type, filter_locations_by_tags

# Get all food-related locations
food_locations = filter_locations_by_type(locations, ["restaurant", "cafe", "bar"])

# Get all historic sites
historic_sites = filter_locations_by_tags(locations, ["historic"])

# Create maps for each category
show_locations_grouped(food_locations, "food_map.html")
show_locations_grouped(historic_sites, "historic_map.html")
```

### 4. Complete Workflow

```python
from map_locations import (
    load_locations_from_yaml,
    validate_location_data,
    get_location_summary,
    filter_locations_by_type,
    show_locations_grouped,
    export_to_all_formats,
)

# Load and validate
locations = load_locations_from_yaml("locations.yaml")
issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Data has issues, please fix before proceeding")
    exit(1)

# Analyze
summary = get_location_summary(locations)
print(f"✅ Loaded {summary['total_count']} valid locations")

# Filter and visualize
museums = filter_locations_by_type(locations, ["museum", "gallery"])
show_locations_grouped(museums, "museums_map.html")

# Export
export_to_all_formats(locations, "exports/complete_dataset")
print("✅ All exports completed")
```

## Data Validation

The `validate_location_data` function returns a dictionary with validation issues:

```python
{
    "missing_required": ["Location 'Eiffel Tower' missing required field 'type'"],
    "invalid_coordinates": ["Location 'Invalid Place' has coordinates outside valid range"],
    "invalid_dates": ["Location 'Old Place' has invalid date format"],
    "duplicate_names": ["Location 'Duplicate Name' appears multiple times"]
}
```

### Validation Categories

- **missing_required**: Locations missing required fields (name, type, latitude, longitude)
- **invalid_coordinates**: Coordinates outside valid ranges (lat: -90 to 90, lon: -180 to 180)
- **invalid_dates**: Date fields with invalid format (should be YYYY-MM-DD)
- **duplicate_names**: Multiple locations with the same name

## Error Handling

### Common Error Patterns

```python
from map_locations import load_locations_from_yaml, validate_location_data
import sys

try:
    # Load data
    locations = load_locations_from_yaml("locations.yaml")

    # Validate
    issues = validate_location_data(locations)
    if any(issues.values()):
        print("❌ Validation failed:")
        for category, problems in issues.items():
            if problems:
                print(f"  {category}: {len(problems)} issues")
        sys.exit(1)

    # Process data
    summary = get_location_summary(locations)
    print(f"✅ Successfully processed {summary['total_count']} locations")

except FileNotFoundError:
    print("❌ File not found: locations.yaml")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
```

### Graceful Degradation

```python
from map_locations import load_locations_from_yaml, filter_locations_by_type

# Load data with fallback
try:
    locations = load_locations_from_yaml("user_data.yaml")
except FileNotFoundError:
    print("⚠️ User data not found, using sample data")
    locations = create_sample_locations()

# Filter with error handling
try:
    restaurants = filter_locations_by_type(locations, ["restaurant"])
    if not restaurants:
        print("⚠️ No restaurants found, showing all locations")
        restaurants = locations
except Exception as e:
    print(f"⚠️ Error filtering locations: {e}")
    restaurants = locations
```

## Best Practices

### 1. Always Validate Data

```python
# Good practice
locations = load_locations_from_yaml("data.yaml")
issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Cannot proceed with invalid data")
    return

# Process validated data
summary = get_location_summary(locations)
```

### 2. Use Type Hints

```python
from typing import List, Dict, Any
from map_locations import Location

def process_locations(locations: List[Location]) -> Dict[str, Any]:
    """Process locations with proper type hints."""
    return get_location_summary(locations)
```

### 3. Handle Edge Cases

```python
def safe_filter_locations(locations: List[Location], types: List[str]) -> List[Location]:
    """Safely filter locations with error handling."""
    if not locations:
        return []

    if not types:
        return locations

    try:
        return filter_locations_by_type(locations, types)
    except Exception as e:
        print(f"⚠️ Error filtering: {e}")
        return locations
```

### 4. Provide Meaningful Output

```python
def create_location_report(locations: List[Location]) -> str:
    """Create a human-readable report."""
    summary = get_location_summary(locations)

    report = f"""
Location Report
==============
Total Locations: {summary['total_count']}
Types: {', '.join(summary['types'])}
Top Types: {dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:3])}
Neighborhoods: {len(summary['neighborhoods'])}
Tags: {len(summary['tags'])}
"""
    return report
```

### 5. Use Consistent Naming

```python
# Good: Clear, descriptive names
restaurant_locations = filter_locations_by_type(locations, ["restaurant", "cafe"])
historic_sites = filter_locations_by_tags(locations, ["historic", "landmark"])

# Good: Consistent file naming
show_locations_grouped(restaurant_locations, "restaurants_map.html")
show_locations_grouped(historic_sites, "historic_sites_map.html")
```

## Advanced Patterns

### Batch Processing

```python
def process_multiple_datasets(file_paths: List[str]) -> Dict[str, Any]:
    """Process multiple location datasets."""
    results = {}

    for file_path in file_paths:
        try:
            locations = load_locations_from_yaml(file_path)
            summary = get_location_summary(locations)
            results[file_path] = summary
        except Exception as e:
            results[file_path] = {"error": str(e)}

    return results
```

### Conditional Processing

```python
def smart_location_processing(locations: List[Location]) -> str:
    """Intelligently process locations based on content."""
    summary = get_location_summary(locations)

    if summary['total_count'] == 0:
        return "No locations to process"

    if len(summary['types']) == 1:
        # Single type - create simple map
        return show_locations_grouped(locations, "simple_map.html")

    if summary['total_count'] > 100:
        # Large dataset - create filtered views
        top_types = dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:3])
        for location_type in top_types:
            filtered = filter_locations_by_type(locations, [location_type])
            show_locations_grouped(filtered, f"{location_type}_map.html")
        return "Created filtered maps for top types"

    # Default - create comprehensive map
    return show_locations_grouped(locations, "comprehensive_map.html")
```

### Error Recovery

```python
def robust_location_processing(locations: List[Location]) -> Dict[str, Any]:
    """Process locations with comprehensive error handling."""
    result = {"success": False, "output_files": [], "errors": []}

    try:
        # Validate
        issues = validate_location_data(locations)
        if issues['missing_required']:
            result["errors"].extend(issues['missing_required'])
            return result

        # Create main map
        main_map = show_locations_grouped(locations, "main_map.html")
        result["output_files"].append(main_map)

        # Export data
        export_to_all_formats(locations, "exports/")
        result["output_files"].extend([
            "exports/locations.json",
            "exports/locations.csv",
            "exports/locations.geojson",
            "exports/locations.kml"
        ])

        result["success"] = True

    except Exception as e:
        result["errors"].append(f"Processing error: {e}")

    return result
```
