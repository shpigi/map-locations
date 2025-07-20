# Map Locations

A Python library and CLI tool for mapping locations with interactive filtering and visualization capabilities.

[![CI](https://github.com/shpigi/map-locations/workflows/CI/badge.svg)](https://github.com/shpigi/map-locations/actions)
[![Codecov](https://codecov.io/gh/shpigi/map-locations/branch/main/graph/badge.svg)](https://codecov.io/gh/shpigi/map-locations)

**Author:** Lavi Shpigelman

## Features

- 📍 **Interactive Maps**: Create beautiful, interactive maps using Folium
- 🗺️ **Multiple Tile Providers**: Support for OpenStreetMap, Google Maps, and Google Satellite
- 🏷️ **Tag-based Filtering**: Filter locations by tags and types
- 🎨 **Color-coded Types**: Different location types are displayed with distinct colors
- 📝 **Toggle Labels**: Show/hide location names on the map
- 📊 **Multiple Export Formats**: Export to KML, GeoJSON, and HTML
- 📁 **YAML Configuration**: Simple YAML format for location data
- 🖥️ **CLI Interface**: Command-line tool for easy map generation

## Installation

### From PyPI (when published)

```bash
pip install map-locations
```

### From Source

```bash
# Clone the repository
git clone https://github.com/shpigi/map-locations.git
cd map-locations

# Install in development mode
pip install -e .

# Or install with development dependencies
pip install -e ".[dev]"
```

### Development Setup

```bash
# Install with all development tools
make install-dev

# Set up pre-commit hooks
make setup-dev
```

## Quick Start

### 1. Create a locations file

Create a YAML file with your locations:

```yaml
locations:
  - name: "Galerie Vivienne"
    type: "passage"
    latitude: 48.8667
    longitude: 2.3397
    tags: ["historic"]
    neighborhood: "2nd arrondissement"
    date_added: "2025-07-19"
    date_of_visit: "YYYY-MM-DD"

  - name: "Passage des Panoramas"
    type: "passage"
    latitude: 48.87111
    longitude: 2.34167
    tags: ["historic"]
    neighborhood: "2nd arrondissement"
    date_added: "2025-07-19"
    date_of_visit: "YYYY-MM-DD"
```

### 2. Generate a map

```bash
# Using the CLI tool
map-locations locations.yaml --output map.html

# Or using Python
python -c "
from map_locations import load_locations_from_yaml, show_locations_grouped
locations = load_locations_from_yaml('locations.yaml')
show_locations_grouped(locations, map_filename='map.html')
"
```

### 3. Export to different formats

```bash
# Export to all formats (JSON, CSV, GeoJSON, KML, HTML)
map-locations locations.yaml --format all --output exports/locations

# Export to specific format
map-locations locations.yaml --format json --output exports/locations.json
map-locations locations.yaml --format csv --output exports/locations.csv
map-locations locations.yaml --format geojson --output exports/locations.geojson
map-locations locations.yaml --format kml --output exports/locations.kml
map-locations locations.yaml --format html --output exports/locations.html
```

### 4. Import into Google My Maps

You can easily import your exported KML files into [Google My Maps](https://www.google.com/maps/d/u/0/) for additional features. See the [Google My Maps Integration](#google-my-maps-integration) section below for detailed instructions.

## For AI Agents

This package is designed to be AI-agent friendly with comprehensive type hints, clear function signatures, and utility functions for common operations.

### Core Data Structure

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

### Quick AI Agent Usage Examples

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

### Available Functions for AI Agents

#### Data Loading and Validation
- `load_locations_from_yaml(yaml_path: str) -> List[Location]`
- `create_sample_locations() -> List[Location]`
- `validate_location_data(locations: List[Location]) -> Dict[str, List[str]]`

#### Data Analysis
- `get_location_summary(locations: List[Location]) -> Dict[str, Any]`
- `get_available_types(locations: List[Location]) -> List[str]`
- `get_available_tags(locations: List[Location]) -> List[str]`
- `get_available_neighborhoods(locations: List[Location]) -> List[str]`

#### Filtering
- `filter_locations_by_type(locations: List[Location], types: List[str]) -> List[Location]`
- `filter_locations_by_tags(locations: List[Location], tags: List[str]) -> List[Location]`
- `filter_locations_by_neighborhood(locations: List[Location], neighborhoods: List[str]) -> List[Location]`

#### Visualization
- `show_locations_grouped(locations: List[Location], group_by: str = "type", map_filename: str = "map.html")`
- `show_locations_with_filtering(locations: List[Location], map_filename: str = "map.html")`
- `show_locations_with_google_maps(locations: List[Location], map_filename: str = "map.html")`

#### Export
- `export_to_json(locations: List[Location], output_path: str)`
- `export_to_csv(locations: List[Location], output_path: str)`
- `export_to_geojson(locations: List[Location], output_path: str)`
- `export_to_kml(locations: List[Location], output_path: str)`
- `export_to_all_formats(locations: List[Location], base_path: str)`

### Common AI Agent Workflows

#### 1. Data Exploration
```python
from map_locations import load_locations_from_yaml, get_location_summary

locations = load_locations_from_yaml("data.yaml")
summary = get_location_summary(locations)
print(f"Dataset contains {summary['total_count']} locations")
print(f"Types: {summary['types']}")
print(f"Top types: {dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:5])}")
```

#### 2. Data Validation
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

#### 3. Filtered Analysis
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

#### 4. Complete Workflow
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

## Tile Providers

The library supports multiple tile providers for different map styles:

### OpenStreetMap (Default)
- **Cost**: Free
- **Usage**: No API key required
- **Best for**: General use, open data

### Google Maps
- **Cost**: Free for personal use, requires API key for commercial use
- **Usage**: No API key required for personal use
- **Best for**: Familiar interface, detailed street data

### Google Satellite
- **Cost**: Free for personal use, requires API key for commercial use
- **Usage**: No API key required for personal use
- **Best for**: Aerial views, terrain analysis

**Note**: Google Maps tiles are free for personal use but may require an API key and payment for commercial use or high-volume usage. For commercial applications, consider using the official Google Maps JavaScript API.

## Location Data Format

Each location in your YAML file should include:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Location name |
| `type` | string | ✅ | Location type (determines color) |
| `latitude` | float | ✅ | Latitude coordinate |
| `longitude` | float | ✅ | Longitude coordinate |
| `tags` | list | ❌ | Array of tags for filtering |
| `neighborhood` | string | ❌ | Neighborhood or area |
| `date_added` | string | ❌ | Date added to collection |
| `date_of_visit` | string | ❌ | date of visit (use "YYYY-MM-DD") |

### Example Location Entry

```yaml
- name: "Passage du Grand Cerf"
  type: "passage"
  latitude: 48.86483
  longitude: 2.34933
  tags: ["architecture", "glass roof"]
  neighborhood: "2nd arrondissement"
  date_added: "2025-07-19"
  date_of_visit: "YYYY-MM-DD"
```

## CLI Usage

The CLI supports multiple formats with a single command structure:

### Available Formats

- `html` - Interactive HTML map (default)
- `json` - JSON format
- `csv` - CSV format
- `geojson` - GeoJSON format
- `kml` - KML format with grouped folders for Google Maps
- `all` - All formats including HTML

### Basic Usage

```bash
# Create HTML map (default)
map-locations locations.yaml --output map.html

# Export to specific format
map-locations locations.yaml --format json --output locations.json
map-locations locations.yaml --format kml --output locations.kml

# Export to all formats (including HTML)
map-locations locations.yaml --format all --output locations
```

### Advanced Options

```bash
# Create map with Google Maps tiles
map-locations locations.yaml --tile-provider google_maps --output map.html

# Create map with Google Satellite view
map-locations locations.yaml --tile-provider google_satellite --output map.html

# Group by different fields
map-locations locations.yaml --group-by neighborhood --output map.html
map-locations locations.yaml --group-by date_added --output map.html
```

**See also**: [Grouping Options](#grouping-options) and [Tile Provider Options](#tile-provider-options) for more examples.

**Note**: For importing into Google My Maps, use the KML format. See [Google My Maps Integration](#google-my-maps-integration) for details.

### Google My Maps Integration

Export your locations to KML format and import them into [Google My Maps](https://www.google.com/maps/d/u/0/) for enhanced features:

```bash
# Export to KML for Google My Maps
map-locations locations.yaml --format kml --output my_locations.kml
```

**Steps to import into Google My Maps**:
1. Go to [Google My Maps](https://www.google.com/maps/d/u/0/)
2. Click "Create a new map"
3. Click "Import" in the left panel
4. Upload your KML file
5. Your locations will appear with all details preserved

**Google My Maps Features**:
- 📱 **Mobile Access**: View maps on smartphones and tablets
- 👥 **Sharing**: Share maps via link or email
- 🎨 **Custom Styling**: Change colors, icons, and labels
- 📝 **Collaboration**: Allow others to edit your maps
- 🗺️ **Offline Access**: Download maps for offline use
- 📍 **Custom Markers**: Add custom icons and descriptions
- 🗂️ **Layers**: Organize locations into different layers

### Grouping Options

```bash
# Group by neighborhood (default)
map-locations locations.yaml --group-by neighborhood

# Group by location type
map-locations locations.yaml --group-by type

# Group by date added
map-locations locations.yaml --group-by date_added

# Group by date of visit
map-locations locations.yaml --group-by date_of_visit
```

### Tile Provider Options

```bash
# Use OpenStreetMap (default, free)
map-locations locations.yaml --tile-provider openstreetmap

# Use Google Maps (free for personal use)
map-locations locations.yaml --tile-provider google_maps

# Use Google Satellite (free for personal use)
map-locations locations.yaml --tile-provider google_satellite
```

## Library Usage

### Basic Map Generation

```python
from map_locations import load_locations_from_yaml, show_locations_grouped

# Load locations from YAML
locations = load_locations_from_yaml("locations.yaml")

# Generate interactive map with grouping (defaults to type)
show_locations_grouped(locations, group_by="type", map_filename="map.html")

# Generate map with Google Maps tiles
show_locations_grouped(
    locations,
    group_by="type",
    map_filename="map.html",
    tile_provider="google_maps"
)

# Generate map with Google Satellite view
show_locations_grouped(
    locations,
    group_by="type",
    map_filename="map.html",
    tile_provider="google_satellite"
)
```

### Grouping and Organization

```python
from map_locations import load_locations_from_yaml, show_locations_grouped

locations = load_locations_from_yaml("locations.yaml")

# Group by type (default)
show_locations_grouped(locations, group_by="type", map_filename="type_map.html")

# Group by neighborhood
show_locations_grouped(locations, group_by="neighborhood", map_filename="neighborhood_map.html")

# Group by date added
show_locations_grouped(locations, group_by="date_added", map_filename="date_map.html")
```

**See also**: [Grouping Options](#grouping-options) for CLI examples of all available grouping fields.

### Data Loading

```python
from map_locations import load_locations_from_yaml

# Load locations from YAML file
locations = load_locations_from_yaml("locations.yaml")

# Access location data
for location in locations:
    print(f"Name: {location['name']}")
    print(f"Type: {location.get('type', 'Unknown')}")
    print(f"Tags: {location.get('tags', [])}")
    print(f"Coordinates: {location['latitude']}, {location['longitude']}")
```

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/shpigi/map-locations.git
cd map-locations

# Install with development dependencies
make install-dev

# Set up pre-commit hooks
make setup-dev
```

**Note**: This setup is also covered in the [Installation](#installation) section above.

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
pytest tests/ -v --cov=map_locations --cov-report=html

# Run specific test file
pytest tests/test_core.py -v
```

### Code Quality

```bash
# Format code
make format

# Run linting (pre-commit checks on all files)
make lint

# Run linting on staged files only
make lint-staged
```

### Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality. The hooks will automatically run on every commit and include:

- **Code Formatting**: Black for code formatting, isort for import sorting
- **Linting**: Flake8 for style checking, MyPy for type checking
- **File Checks**: YAML validation, JSON validation, trailing whitespace removal
- **Security**: Private key detection, merge conflict detection

#### Setting up pre-commit hooks:

```bash
# Install pre-commit hooks (automatically done with setup-dev)
make setup-dev

# Or manually:
pre-commit install
```

#### Running pre-commit checks manually:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black

# Run hooks on staged files only
pre-commit run
```



#### Code Style Standards

This project follows strict code quality standards:

- **Line Length**: Maximum 100 characters
- **Formatting**: Black for code formatting, isort for imports
- **Linting**: Flake8 for style checking
- **Type Checking**: MyPy for type validation
- **Documentation**: Google-style docstrings

The pre-commit hooks will automatically enforce these standards.

### Building and Publishing

```bash
# Build the package
make build

# Clean build artifacts
make clean

# Publish to PyPI (requires proper configuration)
make publish
```

### Running Examples

```bash
# Run the basic usage example
python examples/basic_usage.py

# Test the CLI
make test-cli
```

## Map Features

### Interactive Elements

- **Clickable Markers**: Click on any location to see detailed popup with name, type, tags, and dates
- **Zoom Controls**: Zoom in/out with mouse wheel or controls
- **Pan Navigation**: Click and drag to move around the map
- **Fullscreen Mode**: Toggle fullscreen view
- **Layer Control**: Toggle visibility of different groups with the layer control panel

### Color Coding

Different groups are automatically assigned colors from a predefined color palette:

- **Group Colors**: Each group (neighborhood, type, etc.) gets a unique color
- **Color Palette**: Red, blue, green, purple, orange, darkred, lightred, beige, darkblue, darkgreen, cadetblue
- **Automatic Cycling**: Colors cycle through the palette for multiple groups
- **Fallback**: Gray color for additional groups beyond the palette

### Popup Information

- **Detailed Popups**: Click any marker to see comprehensive information including:
  - Location name
  - Type
  - Tags
  - Date added
  - date of visit
- **Tooltips**: Hover over markers to see location names
- **Layer Control**: Toggle visibility of different groups using the layer control panel

## Configuration

### Grouping Options

The `show_locations_grouped` function allows you to group locations by any field in your YAML:

```python
from map_locations import load_locations_from_yaml, show_locations_grouped

locations = load_locations_from_yaml("locations.yaml")

# Group by any field
show_locations_grouped(locations, group_by="type")          # By type (default)
show_locations_grouped(locations, group_by="neighborhood")  # By area
show_locations_grouped(locations, group_by="date_added")    # By date
show_locations_grouped(locations, group_by="tags")          # By tags
```

### Map Styling

```python
from map_locations import load_locations_from_yaml, show_locations_grouped

locations = load_locations_from_yaml("locations.yaml")

# Custom map options
show_locations_grouped(
    locations,
    group_by="type",
    map_filename="custom_map.html"
)
```

**See also**: [Tile Providers](#tile-providers) for available tile provider options and [Tile Provider Options](#tile-provider-options) for CLI examples.

## Examples

### Paris Passages Map

The included example shows historic passages in Paris:

```bash
# Generate the Paris passages map grouped by type (default)
map-locations generate --input map_locations/maps/passages/locations.yaml --group-by type --output passages_map.html
```

This creates an interactive map of Paris's historic covered passages with:
- Locations grouped by type (default)
- Color-coded groups with layer controls
- Detailed popups showing name, type, tags, and dates
- Interactive layer panel to toggle group visibility

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Folium](https://python-visualization.github.io/folium/) for interactive maps
- Uses [SimpleKML](https://simplekml.readthedocs.io/) for KML export
- Inspired by the historic passages of Paris
