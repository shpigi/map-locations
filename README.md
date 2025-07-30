# Map Locations

A Python library and CLI tool for mapping locations with interactive filtering and visualization capabilities, plus AI-powered location extraction from text.

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

# Create mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html
```

### AI-Powered Location Extraction
```bash
# Extract locations from text using AI
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml

# Process with URL exploration
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls

# Process with deduplication
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --deduplicate
```

### Open the map in your browser and explore!

## ✨ Features

### Core Mapping Features
- 📍 **Interactive Maps**: Create beautiful, interactive maps using Folium
- 🗺️ **Multiple Tile Providers**: Support for OpenStreetMap, Google Maps, and Google Satellite
- 🏷️ **Tag-based Filtering**: Filter locations by tags and types
- 🎨 **Color-coded Types**: Different location types are displayed with distinct colors
- 📝 **Toggle Labels**: Show/hide location names on the map
- 📊 **Multiple Export Formats**: Export to KML, GeoJSON, HTML, JSON, CSV
- 📁 **YAML Configuration**: Simple YAML format for location data
- 🖥️ **CLI Interface**: Command-line tool for easy map generation
- 📱 **Mobile Optimization**: Mobile-optimized layouts with collapsible controls

### AI-Powered Features
- 🤖 **AI Location Extraction**: Extract locations from text using OpenAI LLM
- 🌐 **URL Processing**: Automatically extract location info from web pages
- 🔄 **Smart Deduplication**: Intelligent duplicate detection and merging
- 📈 **Confidence Scoring**: AI-generated confidence scores for extracted locations
- 🔍 **Source Tracking**: Exact text spans and URLs preserved for debugging
- 📝 **Comprehensive Tracing**: Complete logging of all AI operations
- 🗺️ **LLM Geocoding**: AI-assisted geocoding as fallback for location coordinates
- 🌍 **Global Location Support**: Worldwide compatibility with improved geocoding

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

# Create mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html

# Export to different formats
map-locations locations.yaml --format kml --output locations.kml
map-locations locations.yaml --format all --output exports/

# Use different tile providers
map-locations locations.yaml --tile-provider google_maps --output map.html
map-locations locations.yaml --tile-provider google_satellite --output map.html

# Mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html
```

### AI Processing
```bash
# Extract locations from text
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml

# Process with URL exploration
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls

# Process with deduplication
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --deduplicate

# Complete workflow
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls --deduplicate
```

### Python Library
```python
from map_locations import load_locations_from_yaml, show_locations_grouped

# Load locations
locations = load_locations_from_yaml("locations.yaml")

# Create interactive map
show_locations_grouped(locations, map_filename="map.html")

# Create mobile-optimized map
show_locations_grouped(locations, map_filename="mobile_map.html", mobile=True)
```

## 🗺️ Map Features

- **Interactive Elements**: Clickable markers, zoom controls, pan navigation
- **Layer Control**: Toggle visibility of different groups
- **Color Coding**: Automatic color assignment for different location types
- **Detailed Popups**: Click markers to see comprehensive information
- **Multiple Tile Providers**: OpenStreetMap, Google Maps, Google Satellite
- **Mobile Optimization**: Collapsible controls, clickable phone numbers, optimized layout

## 📊 Export Formats

- **HTML**: Interactive web maps with Folium
- **KML**: Import into Google My Maps and other mapping apps
- **GeoJSON**: Standard geospatial format
- **JSON**: Structured data export
- **CSV**: Spreadsheet-compatible format

## 🤖 AI Features

### Location Extraction
- **Text Processing**: Extract locations from any text using OpenAI LLM
- **Chunked Processing**: Handle large files efficiently (100-line chunks)
- **YAML Output**: Generate structured location data automatically
- **Error Recovery**: Auto-fix malformed responses and partial extraction

### URL Processing
- **Web Scraping**: Extract location info from web pages
- **Content Cleaning**: Remove navigation/footer content for cleaner processing
- **Rate Limiting**: Respectful web scraping with configurable delays
- **Backup System**: Automatic backup creation and restoration
- **Multi-threaded Verification**: Improved URL checking performance

### Deduplication
- **Smart Detection**: Multi-level similarity scoring (name, type, description)
- **Confidence Merging**: Weighted strategies for combining duplicates
- **Type Compatibility**: Understands related types (museum/gallery, etc.)
- **Graph Clustering**: Efficient Union-Find algorithm for duplicate grouping

### Geocoding
- **LLM-Assisted Geocoding**: AI-powered coordinate extraction as fallback
- **Global Location Support**: Worldwide compatibility without city assumptions
- **Confidence Scoring**: Reliability metrics for geocoding results
- **JSON Response Parsing**: Robust coordinate validation and extraction

### Quality Assurance
- **Confidence Scoring**: 0.1-0.9 range with source tie-back
- **Comprehensive Tracing**: Complete logging of all operations
- **Validation**: Required field checking and format validation
- **Performance Monitoring**: Timing and memory usage tracking
- **Honest Defaults**: Real validation status and confidence scores only

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
map_locations_ai/                 # AI processing package
├── map_locations_ai/
│   ├── pipeline.py              # Main AI processing pipeline
│   ├── deduplicator.py          # Smart deduplication
│   ├── url_processor.py         # URL processing
│   ├── processors/              # Modular processing components
│   │   ├── llm_processor.py     # OpenAI integration
│   │   ├── yaml_processor.py    # YAML handling
│   │   ├── enrichment_processor.py # Location enrichment
│   │   ├── geocoding_service.py # Geocoding with LLM fallback
│   │   └── ...                  # Other processors
│   ├── config.yaml              # AI configuration
│   └── agent_prompt.txt         # LLM prompts
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
- Powered by [OpenAI](https://openai.com/) for AI location extraction
- Inspired by the historic passages of Paris
