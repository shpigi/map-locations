# API Reference

Complete API documentation for the Map Locations package.

## Table of Contents

- [Core Functions](#core-functions)
- [Data Loading](#data-loading)
- [Data Analysis](#data-analysis)
- [Filtering](#filtering)
- [Visualization](#visualization)
- [Export Functions](#export-functions)
- [AI Processing](#ai-processing)
- [Data Models](#data-models)

## Core Functions

### `load_locations_from_yaml(yaml_path: str) -> List[Location]`

Load locations from a YAML file.

**Parameters:**
- `yaml_path` (str): Path to the YAML file containing location data

**Returns:**
- `List[Location]`: List of location dictionaries

**Raises:**
- `FileNotFoundError`: If the YAML file doesn't exist
- `yaml.YAMLError`: If the YAML file is malformed
- `KeyError`: If the YAML file doesn't contain a 'locations' key

**Example:**
```python
from map_locations import load_locations_from_yaml

locations = load_locations_from_yaml("my_locations.yaml")
print(f"Loaded {len(locations)} locations")
```

### `create_sample_locations() -> List[Location]`

Create sample location data for testing and demonstration.

**Returns:**
- `List[Location]`: List of sample location dictionaries

**Example:**
```python
from map_locations import create_sample_locations

sample_locations = create_sample_locations()
print(f"Created {len(sample_locations)} sample locations")
```

## Data Analysis

### `get_location_summary(locations: List[Location]) -> Dict[str, Any]`

Get a comprehensive summary of location data.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries

**Returns:**
- `Dict[str, Any]`: Summary containing:
  - `total_count`: Total number of locations
  - `types`: List of unique location types
  - `type_counts`: Dictionary of type counts
  - `tags`: List of unique tags
  - `neighborhoods`: List of unique neighborhoods
  - `date_ranges`: Date range information

**Example:**
```python
from map_locations import get_location_summary

summary = get_location_summary(locations)
print(f"Total: {summary['total_count']}")
print(f"Types: {summary['types']}")
print(f"Top types: {summary['type_counts']}")
```

### `get_available_types(locations: List[Location]) -> List[str]`

Get list of unique location types.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries

**Returns:**
- `List[str]`: List of unique location types

**Example:**
```python
from map_locations import get_available_types

types = get_available_types(locations)
print(f"Available types: {types}")
```

### `get_available_tags(locations: List[Location]) -> List[str]`

Get list of unique tags.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries

**Returns:**
- `List[str]`: List of unique tags

**Example:**
```python
from map_locations import get_available_tags

tags = get_available_tags(locations)
print(f"Available tags: {tags}")
```

### `get_available_neighborhoods(locations: List[Location]) -> List[str]`

Get list of unique neighborhoods.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries

**Returns:**
- `List[str]`: List of unique neighborhoods

**Example:**
```python
from map_locations import get_available_neighborhoods

neighborhoods = get_available_neighborhoods(locations)
print(f"Available neighborhoods: {neighborhoods}")
```

## Data Validation

### `validate_location_data(locations: List[Location]) -> Dict[str, List[str]]`

Validate location data for issues.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries

**Returns:**
- `Dict[str, List[str]]`: Dictionary of validation issues:
  - `missing_required`: Locations missing required fields
  - `invalid_coordinates`: Locations with invalid coordinates
  - `invalid_dates`: Locations with invalid date formats
  - `duplicate_names`: Duplicate location names

**Example:**
```python
from map_locations import validate_location_data

issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Missing required fields:", issues['missing_required'])
if issues['invalid_coordinates']:
    print("❌ Invalid coordinates:", issues['invalid_coordinates'])
```

## Filtering

### `filter_locations_by_type(locations: List[Location], types: List[str]) -> List[Location]`

Filter locations by type.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `types` (List[str]): List of types to filter by

**Returns:**
- `List[Location]`: Filtered list of locations

**Example:**
```python
from map_locations import filter_locations_by_type

restaurants = filter_locations_by_type(locations, ["restaurant", "cafe"])
print(f"Found {len(restaurants)} food locations")
```

### `filter_locations_by_tags(locations: List[Location], tags: List[str]) -> List[Location]`

Filter locations by tags.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `tags` (List[str]): List of tags to filter by

**Returns:**
- `List[Location]`: Filtered list of locations

**Example:**
```python
from map_locations import filter_locations_by_tags

historic_sites = filter_locations_by_tags(locations, ["historic", "landmark"])
print(f"Found {len(historic_sites)} historic sites")
```

### `filter_locations_by_neighborhood(locations: List[Location], neighborhoods: List[str]) -> List[Location]`

Filter locations by neighborhood.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `neighborhoods` (List[str]): List of neighborhoods to filter by

**Returns:**
- `List[Location]`: Filtered list of locations

**Example:**
```python
from map_locations import filter_locations_by_neighborhood

downtown_locations = filter_locations_by_neighborhood(locations, ["Downtown", "City Center"])
print(f"Found {len(downtown_locations)} downtown locations")
```

## Visualization

### `show_locations_grouped(locations: List[Location], group_by: str = "type", map_filename: str = "map.html", tile_provider: str = "openstreetmap", filter_types: Optional[List[str]] = None, mobile: bool = False) -> str`

Create an interactive map with grouped locations.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `group_by` (str): Field to group by ("type", "neighborhood", "date_added", "date_of_visit")
- `map_filename` (str): Output filename for the HTML map
- `tile_provider` (str): Tile provider ("openstreetmap", "google_maps", "google_satellite")
- `filter_types` (Optional[List[str]]): List of location types to include
- `mobile` (bool): Enable mobile-optimized popups and layout

**Returns:**
- `str`: Path to the generated HTML file

**Example:**
```python
from map_locations import show_locations_grouped

# Create map grouped by type
map_file = show_locations_grouped(locations, group_by="type", map_filename="type_map.html")

# Create mobile-optimized map
map_file = show_locations_grouped(locations, group_by="type", map_filename="mobile_map.html", mobile=True)

# Create map with Google Maps tiles
map_file = show_locations_grouped(
    locations,
    group_by="neighborhood",
    map_filename="neighborhood_map.html",
    tile_provider="google_maps"
)

# Create mobile map with filtering
map_file = show_locations_grouped(
    locations,
    group_by="type",
    map_filename="mobile_filtered_map.html",
    filter_types=["restaurant", "cafe"],
    mobile=True
)
```

### `show_locations_with_filtering(locations: List[Location], map_filename: str = "map.html", tile_provider: str = "openstreetmap", filter_types: Optional[List[str]] = None, group_by: str = "type", mobile: bool = False) -> str`

Create an interactive map with filtering capabilities.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `map_filename` (str): Output filename for the HTML map
- `tile_provider` (str): Tile provider ("openstreetmap", "google_maps", "google_satellite")
- `filter_types` (Optional[List[str]]): List of location types to include
- `group_by` (str): Field to group markers by
- `mobile` (bool): Enable mobile-optimized popups and layout

**Returns:**
- `str`: Path to the generated HTML file

**Example:**
```python
from map_locations import show_locations_with_filtering

# Create filtered map
map_file = show_locations_with_filtering(locations, "filtered_map.html")

# Create mobile filtered map
map_file = show_locations_with_filtering(locations, "mobile_filtered_map.html", mobile=True)
```

### `show_locations_with_advanced_filtering(locations: List[Location], map_filename: str = "map.html", tile_provider: str = "openstreetmap", filter_types: Optional[List[str]] = None, mobile: bool = False) -> str`

Create an interactive map with advanced filtering capabilities using dropdown controls.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `map_filename` (str): Output filename for the HTML map
- `tile_provider` (str): Tile provider ("openstreetmap", "google_maps", "google_satellite")
- `filter_types` (Optional[List[str]]): List of location types to pre-filter
- `mobile` (bool): Enable mobile-optimized popups and collapsible filtering controls

**Returns:**
- `str`: Path to the generated HTML file

**Example:**
```python
from map_locations import show_locations_with_advanced_filtering

# Create advanced filtering map
map_file = show_locations_with_advanced_filtering(locations, "advanced_map.html")

# Create mobile advanced filtering map
map_file = show_locations_with_advanced_filtering(locations, "mobile_advanced_map.html", mobile=True)
```

### `show_locations_with_google_maps(locations: List[Location], group_by: str = "type", map_filename: str = "map.html", satellite: bool = False, mobile: bool = False) -> str`

Create an interactive map using Google Maps tiles.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `group_by` (str): Field to group markers by
- `map_filename` (str): Output filename for the HTML map
- `satellite` (bool): Use satellite view instead of street view
- `mobile` (bool): Enable mobile-optimized popups and layout

**Returns:**
- `str`: Path to the generated HTML file

**Example:**
```python
from map_locations import show_locations_with_google_maps

# Create Google Maps map
map_file = show_locations_with_google_maps(locations, "google_maps.html")

# Create mobile Google Maps map
map_file = show_locations_with_google_maps(locations, "mobile_google_maps.html", mobile=True)

# Create satellite view
map_file = show_locations_with_google_maps(locations, "satellite_map.html", satellite=True)
```

## Export Functions

### `export_to_json(locations: List[Location], output_path: str) -> str`

Export locations to JSON format.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to the generated JSON file

**Example:**
```python
from map_locations import export_to_json

json_file = export_to_json(locations, "locations.json")
print(f"Exported to {json_file}")
```

### `export_to_csv(locations: List[Location], output_path: str) -> str`

Export locations to CSV format.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to the generated CSV file

**Example:**
```python
from map_locations import export_to_csv

csv_file = export_to_csv(locations, "locations.csv")
print(f"Exported to {csv_file}")
```

### `export_to_geojson(locations: List[Location], output_path: str) -> str`

Export locations to GeoJSON format.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to the generated GeoJSON file

**Example:**
```python
from map_locations import export_to_geojson

geojson_file = export_to_geojson(locations, "locations.geojson")
print(f"Exported to {geojson_file}")
```

### `export_to_kml(locations: List[Location], output_path: str) -> str`

Export locations to KML format.

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `output_path` (str): Output file path

**Returns:**
- `str`: Path to the generated KML file

**Example:**
```python
from map_locations import export_to_kml

kml_file = export_to_kml(locations, "locations.kml")
print(f"Exported to {kml_file}")
```

### `export_to_all_formats(locations: List[Location], base_path: str) -> List[str]`

Export locations to all formats (JSON, CSV, GeoJSON, KML, HTML).

**Parameters:**
- `locations` (List[Location]): List of location dictionaries
- `base_path` (str): Base path for output files (without extension)

**Returns:**
- `List[str]`: List of generated file paths

**Example:**
```python
from map_locations import export_to_all_formats

files = export_to_all_formats(locations, "exports/my_locations")
print(f"Exported {len(files)} files")
```

## AI Processing

The AI processing functions are available through the `map_locations_ai` module.

### `LocationExtractionPipeline`

Main AI processing pipeline for extracting locations from text.

**Parameters:**
- `config_path` (str): Path to configuration file

**Methods:**
- `process_file(input_file: str) -> Dict[str, Any]`: Process a text file
- `process_file_with_urls(input_file: str) -> Dict[str, Any]`: Process with URL exploration
- `process_file_with_deduplication(input_file: str) -> Dict[str, Any]`: Process with deduplication

**Example:**
```python
from map_locations_ai.pipeline import LocationExtractionPipeline

# Initialize pipeline
pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")

# Process text file
result = pipeline.process_file("input.txt")
print(f"Extracted {result['total_locations']} locations")

# Process with URL exploration
result = pipeline.process_file_with_urls("input.txt")
print(f"Processed {result['total_chunks']} chunks")

# Process with deduplication
result = pipeline.process_file_with_deduplication("input.txt")
print(f"Final locations after deduplication: {result['total_locations']}")
```

### `Deduplicator`

Smart deduplication for location data.

**Parameters:**
- `config_path` (str): Path to configuration file

**Methods:**
- `deduplicate_locations(locations: List[Location]) -> List[Location]`: Remove duplicates
- `find_duplicates(locations: List[Location]) -> List[List[int]]`: Find duplicate groups
- `merge_locations(location1: Location, location2: Location) -> Location`: Merge two locations

**Example:**
```python
from map_locations_ai.deduplicator import Deduplicator

# Initialize deduplicator
deduplicator = Deduplicator("map_locations_ai/config.yaml")

# Deduplicate locations
unique_locations = deduplicator.deduplicate_locations(locations)
print(f"Reduced from {len(locations)} to {len(unique_locations)} locations")
```

### `URLProcessor`

Process URLs to extract location information.

**Parameters:**
- `config_path` (str): Path to configuration file

**Methods:**
- `process_urls_in_chunks() -> None`: Process URLs in existing chunks
- `extract_from_url(url: str) -> Dict[str, Any]`: Extract location info from URL
- `clean_web_content(content: str) -> str`: Clean web page content

**Example:**
```python
from map_locations_ai.url_processor import URLProcessor

# Initialize URL processor
url_processor = URLProcessor("map_locations_ai/config.yaml")

# Process URLs in chunks
url_processor.process_urls_in_chunks()

# Extract from specific URL
info = url_processor.extract_from_url("https://example.com/location")
print(f"Extracted: {info['name']}")
```

## Data Models

### `Location` (TypedDict)

Location data structure.

**Fields:**
- `name` (str): Location name (required)
- `type` (str): Location type/category (required)
- `latitude` (float): Latitude coordinate (required)
- `longitude` (float): Longitude coordinate (required)
- `tags` (List[str]): List of tags for filtering (optional)
- `neighborhood` (str): Neighborhood or area name (optional)
- `date_added` (str): Date when added to collection (optional, YYYY-MM-DD)
- `date_of_visit` (str): Date of visit (optional, YYYY-MM-DD)
- `description` (str): AI-generated description (optional)
- `source_text` (str): Exact text from AI extraction (optional)
- `confidence` (float): AI confidence score 0.1-0.9 (optional)
- `is_url` (bool): Whether source is a URL (optional)
- `url` (str): Source URL if applicable (optional)
- `address` (str): Full address if available (optional)
- `extraction_method` (str): How location was extracted (optional)

**Example:**
```python
from map_locations import Location

location: Location = {
    "name": "Eiffel Tower",
    "type": "landmark",
    "latitude": 48.8584,
    "longitude": 2.2945,
    "tags": ["historic", "tourist"],
    "neighborhood": "7th arrondissement",
    "date_added": "2025-01-15",
    "date_of_visit": "2025-01-20",
    "description": "Iconic iron lattice tower",
    "source_text": "Eiffel Tower - must see landmark",
    "confidence": 0.9,
    "is_url": False,
    "url": "",
    "address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris",
    "extraction_method": "llm"
}
```

### `LocationList` (Type Alias)

Type alias for a list of locations.

```python
LocationList = List[Location]
```

## Mobile Optimization

The library includes mobile-optimized features for better usability on smartphones and tablets.

### Mobile Features

#### Popup Optimization
- **Narrower Width**: 300px popup width (vs 450px on desktop)
- **Essential Content**: Streamlined information display
- **Clickable Elements**: Phone numbers and website links are clickable
- **Truncated Descriptions**: Long descriptions limited to 100 characters

#### Filtering Controls
- **Collapsible Panel**: Filter panel can be toggled on/off
- **Toggle Button**: Floating filter button in top-left corner
- **Touch-Friendly**: Larger buttons and touch targets
- **Compact Layout**: Smaller fonts and tighter spacing

#### Field Ordering
- **Mobile-Optimized**: Essential fields displayed first
- **Reduced Content**: Less verbose field descriptions
- **Touch Targets**: Larger clickable areas

### Mobile Usage Examples

```python
from map_locations import show_locations_grouped, show_locations_with_advanced_filtering

# Create mobile-optimized map
show_locations_grouped(
    locations,
    map_filename="mobile_map.html",
    mobile=True
)

# Create mobile map with advanced filtering
show_locations_with_advanced_filtering(
    locations,
    map_filename="mobile_advanced_map.html",
    mobile=True
)

# Create mobile map with Google Maps tiles
show_locations_with_google_maps(
    locations,
    map_filename="mobile_google_map.html",
    mobile=True
)
```

### Mobile vs Desktop Comparison

| Feature | Desktop | Mobile |
|---------|---------|--------|
| Popup Width | 450px | 300px |
| Filter Panel | Always visible | Collapsible |
| Filter Button | None | Toggle button |
| Phone Numbers | Text only | Clickable links |
| Website Links | Text only | Clickable links |
| Description Length | Full | Truncated (100 chars) |
| Field Order | Standard | Mobile-optimized |

## Error Handling

### Common Exceptions

- `FileNotFoundError`: When YAML file doesn't exist
- `yaml.YAMLError`: When YAML file is malformed
- `KeyError`: When required YAML structure is missing
- `ValueError`: When coordinates are invalid
- `TypeError`: When data types are incorrect

### Error Handling Example

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
    print(f"✅ Successfully loaded {len(locations)} locations")

except FileNotFoundError:
    print("❌ File not found: locations.yaml")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
```

## Performance Considerations

### Large Datasets

For datasets with many locations (>1000):

1. **Use filtering** to reduce data size before processing
2. **Export to specific formats** rather than all formats
3. **Consider clustering** for visualization
4. **Use batch processing** for multiple files

### Memory Usage

- Location objects are lightweight
- HTML maps can be large for many locations
- Consider streaming for very large datasets
- Use generators for memory-efficient iteration

## Best Practices

### 1. Always Validate Data

```python
locations = load_locations_from_yaml("data.yaml")
issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Cannot proceed with invalid data")
    return
```

### 2. Use Type Hints

```python
from typing import List
from map_locations import Location

def process_locations(locations: List[Location]) -> None:
    """Process locations with proper type hints."""
    summary = get_location_summary(locations)
    print(f"Processed {summary['total_count']} locations")
```

### 3. Handle Edge Cases

```python
def safe_filter(locations: List[Location], types: List[str]) -> List[Location]:
    """Safely filter locations."""
    if not locations or not types:
        return []

    try:
        return filter_locations_by_type(locations, types)
    except Exception as e:
        print(f"⚠️ Error filtering: {e}")
        return []
```

### 4. Provide Meaningful Output

```python
def create_report(locations: List[Location]) -> str:
    """Create a human-readable report."""
    summary = get_location_summary(locations)
    return f"Report: {summary['total_count']} locations, {len(summary['types'])} types"
```

### 5. AI Processing Best Practices

```python
from map_locations_ai.pipeline import LocationExtractionPipeline

def process_with_ai(input_file: str, config_file: str) -> Dict[str, Any]:
    """Process text with AI extraction."""
    try:
        pipeline = LocationExtractionPipeline(config_file)
        result = pipeline.process_file_with_urls(input_file)

        print(f"✅ Extracted {result['total_locations']} locations")
        print(f"📊 Processed {result['total_chunks']} chunks")
        print(f"📝 Trace file: {result['trace_file']}")

        return result
    except Exception as e:
        print(f"❌ AI processing failed: {e}")
        return {"error": str(e)}
```

### 6. Mobile Optimization Best Practices

```python
def create_mobile_map(locations: List[Location], filename: str) -> str:
    """Create a mobile-optimized map."""
    try:
        return show_locations_grouped(
            locations,
            map_filename=filename,
            mobile=True,
            group_by="type"
        )
    except Exception as e:
        print(f"❌ Mobile map creation failed: {e}")
        return ""
```

### 7. Responsive Design Considerations

```python
def create_responsive_maps(locations: List[Location], base_name: str) -> Dict[str, str]:
    """Create both desktop and mobile versions."""
    maps = {}

    # Desktop version
    maps['desktop'] = show_locations_grouped(
        locations,
        map_filename=f"{base_name}_desktop.html",
        mobile=False
    )

    # Mobile version
    maps['mobile'] = show_locations_grouped(
        locations,
        map_filename=f"{base_name}_mobile.html",
        mobile=True
    )

    return maps
```
