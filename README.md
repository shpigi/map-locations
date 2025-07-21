# Map Locations

A Python library and CLI tool for mapping locations with interactive filtering and visualization capabilities.

[![CI](https://github.com/shpigi/map-locations/workflows/CI/badge.svg)](https://github.com/shpigi/map-locations/actions)
[![Codecov](https://codecov.io/gh/shpigi/map-locations/branch/main/graph/badge.svg)](https://codecov.io/gh/shpigi/map-locations)

**Author:** Lavi Shpigelman

## 🚀 Quick Start

### Install
```bash
pip install map-locations
```

### Create Your First Map
```bash
# Create a YAML file with your locations
cat > locations.yaml << EOF
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
    tags: ["historic", "tourist"]
    neighborhood: "7th arrondissement"
EOF

# Generate an interactive map
map-locations locations.yaml --output my_map.html
```

### Open the map in your browser and explore!

## ✨ Features

- 📍 **Interactive Maps**: Create beautiful, interactive maps using Folium
- 🗺️ **Multiple Tile Providers**: Support for OpenStreetMap, Google Maps, and Google Satellite
- 🏷️ **Tag-based Filtering**: Filter locations by tags and types
- 🎨 **Color-coded Types**: Different location types are displayed with distinct colors
- 📝 **Toggle Labels**: Show/hide location names on the map
- 📊 **Multiple Export Formats**: Export to KML, GeoJSON, HTML, JSON, CSV
- 📁 **YAML Configuration**: Simple YAML format for location data
- 🖥️ **CLI Interface**: Command-line tool for easy map generation

## 📖 Documentation

- **[User Guide](docs/user-guide.md)** - Complete guide for using the CLI and library
- **[API Reference](docs/api-reference.md)** - Detailed function documentation
- **[Data Format](docs/data-format.md)** - YAML structure and field descriptions
- **[Export Formats](docs/export-formats.md)** - KML, GeoJSON, HTML, JSON, CSV
- **[AI Agent Guide](docs/ai-agent-guide.md)** - For AI agents and automation
- **[Development Guide](DEVELOPMENT.md)** - For contributors and developers

## 🛠️ Installation

### From PyPI
```bash
pip install map-locations
```

### From Source
```bash
git clone https://github.com/shpigi/map-locations.git
cd map-locations
pip install -e .
```

## 📋 Basic Usage

### CLI Commands
```bash
# Create interactive HTML map
map-locations locations.yaml --output map.html

# Export to different formats
map-locations locations.yaml --format kml --output locations.kml
map-locations locations.yaml --format all --output exports/

# Use different tile providers
map-locations locations.yaml --tile-provider google_maps --output map.html
map-locations locations.yaml --tile-provider google_satellite --output map.html
```

### Python Library
```python
from map_locations import load_locations_from_yaml, show_locations_grouped

# Load locations
locations = load_locations_from_yaml("locations.yaml")

# Create interactive map
show_locations_grouped(locations, map_filename="map.html")
```

## 🗺️ Map Features

- **Interactive Elements**: Clickable markers, zoom controls, pan navigation
- **Layer Control**: Toggle visibility of different groups
- **Color Coding**: Automatic color assignment for different location types
- **Detailed Popups**: Click markers to see comprehensive information
- **Multiple Tile Providers**: OpenStreetMap, Google Maps, Google Satellite

## 📊 Export Formats

- **HTML**: Interactive web maps with Folium
- **KML**: Import into Google My Maps and other mapping apps
- **GeoJSON**: Standard geospatial format
- **JSON**: Structured data export
- **CSV**: Spreadsheet-compatible format

## 🤖 AI Agent Support

This package is designed to be AI-agent friendly with comprehensive type hints, clear function signatures, and utility functions for common operations.

See the **[AI Agent Guide](docs/ai-agent-guide.md)** for detailed documentation.

## 🏗️ Project Structure

```
map_locations/                    # Main package
├── map_locations/
│   ├── core.py                  # Main mapping functionality
│   ├── cli.py                   # CLI interface
│   ├── common/                  # Common utilities
│   │   ├── models.py            # Location data model
│   │   └── formats.py           # YAML serialization
│   └── __init__.py
│
map_locations_ai/                 # AI agent package (TBD)
├── map_locations_ai/
│   ├── agent/                   # AI processing pipeline
│   ├── interfaces/              # CLI and web interfaces
│   └── utils/                   # AI utilities
```

## 🧪 Development

```bash
# Setup development environment
make install-dev
make setup-dev

# Run tests
make test

# Code quality
make lint
make format
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [Folium](https://python-visualization.github.io/folium/) for interactive maps
- Uses [SimpleKML](https://simplekml.readthedocs.io/) for KML export
- Inspired by the historic passages of Paris
