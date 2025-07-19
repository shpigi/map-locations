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
map-locations map locations.yaml --output map.html

# Or using Python
python -c "
from map_locations import load_locations_from_yaml, show_locations_grouped
locations = load_locations_from_yaml('locations.yaml')
show_locations_grouped(locations, map_filename='map.html')
"
```

### 3. Export to different formats

```bash
# Export to all formats (JSON, CSV, GeoJSON, KML)
map-locations export locations.yaml --output exports/locations

# Export to specific format
map-locations export locations.yaml --format json --output exports/locations.json
map-locations export locations.yaml --format csv --output exports/locations.csv
map-locations export locations.yaml --format geojson --output exports/locations.geojson
map-locations export locations.yaml --format kml --output exports/locations.kml
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

### Map Commands

```bash
# Create an interactive map
map-locations map locations.yaml --output map.html

# Create map grouped by type
map-locations map locations.yaml --group-by type --output type_map.html

# Create map grouped by date
map-locations map locations.yaml --group-by date_added --output date_map.html

# Create map with Google Maps tiles
map-locations map locations.yaml --tile-provider google_maps --output map.html

# Create map with Google Satellite view
map-locations map locations.yaml --tile-provider google_satellite --output map.html
```

### Export Commands

```bash
# Export to all formats
map-locations export locations.yaml --output exports/locations

# Export to specific format
map-locations export locations.yaml --format json --output exports/locations.json
map-locations export locations.yaml --format csv --output exports/locations.csv
map-locations export locations.yaml --format geojson --output exports/locations.geojson
map-locations export locations.yaml --format kml --output exports/locations.kml
```

### Grouping Options

```bash
# Group by neighborhood (default)
map-locations map locations.yaml --group-by neighborhood

# Group by location type
map-locations map locations.yaml --group-by type

# Group by date added
map-locations map locations.yaml --group-by date_added

# Group by date of visit
map-locations map locations.yaml --group-by date_of_visit
```

### Tile Provider Options

```bash
# Use OpenStreetMap (default, free)
map-locations map locations.yaml --tile-provider openstreetmap

# Use Google Maps (free for personal use)
map-locations map locations.yaml --tile-provider google_maps

# Use Google Satellite (free for personal use)
map-locations map locations.yaml --tile-provider google_satellite
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

# Run linting
make lint

# Run type checking
mypy map_locations/
```

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

## Development

### Project Structure

```
map_locations/
├── map_locations/
│   ├── __init__.py
│   ├── core.py               # Core functionality
│   └── cli.py               # CLI interface
├── maps/
│   └── passages/
│       ├── locations.yaml    # Example data
│       ├── locations.kml     # Generated KML
│       ├── locations.geojson # Generated GeoJSON
│       └── map.html         # Generated HTML map
├── tests/                   # Test suite
├── README.md               # This file
└── setup.py               # Package configuration
```

### Running Tests

```bash
python -m pytest tests/
```

### Building Documentation

```bash
# Generate API documentation
sphinx-apidoc -o docs/ map_locations/

# Build HTML docs
cd docs && make html
```

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
