# User Guide

Complete guide for using the Map Locations CLI and library.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Data Format](#data-format)
- [CLI Usage](#cli-usage)
- [Mobile Optimization](#mobile-optimization)
- [Library Usage](#library-usage)
- [AI Processing](#ai-processing)
- [Export Formats](#export-formats)
- [Map Features](#map-features)
- [Tile Providers](#tile-providers)
- [Examples](#examples)

## Installation

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

**Note**: The package includes both core mapping functionality and AI features in a unified installation.

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

# Create mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html

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

## AI Processing

The Map Locations package includes powerful AI features for extracting locations from text and enhancing location data.

### AI Location Extraction

Extract locations from any text file using OpenAI's language models:

```bash
# Basic extraction
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml

# Extract with URL processing
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls

# Extract with deduplication
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --deduplicate

# Complete workflow
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls --deduplicate
```

### AI Features

#### Text Processing
- **Chunked Processing**: Handles large files efficiently (100-line chunks with overlap)
- **LLM Integration**: Uses OpenAI GPT-4o-mini for location extraction
- **YAML Output**: Generates structured location data automatically
- **Error Recovery**: Auto-fixes malformed responses and partial extraction

#### URL Processing
- **Web Scraping**: Extracts location info from web pages
- **Content Cleaning**: Removes navigation/footer content for cleaner processing
- **Rate Limiting**: Respectful web scraping with configurable delays
- **Backup System**: Automatic backup creation and restoration
- **Multi-threaded Verification**: Improved URL checking performance

#### Deduplication
- **Smart Detection**: Multi-level similarity scoring (name, type, description)
- **Confidence Merging**: Weighted strategies for combining duplicates
- **Type Compatibility**: Understands related types (museum/gallery, etc.)
- **Graph Clustering**: Efficient Union-Find algorithm for duplicate grouping

#### Geocoding
- **LLM-Assisted Geocoding**: AI-powered coordinate extraction as fallback
- **Global Location Support**: Worldwide compatibility without city assumptions
- **Confidence Scoring**: Reliability metrics for geocoding results
- **JSON Response Parsing**: Robust coordinate validation and extraction

### AI Configuration

The AI features are configured via `map_locations_ai/config.yaml`:

```yaml
# LLM Settings
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 2000
  timeout: 120

# Processing Settings
processing:
  chunk_size: 50
  overlap_size: 10

# Output Settings
output:
  temp_dir: "map_locations_ai/temp"
  trace_dir: "map_locations_ai/trace"

# Deduplication Settings
deduplication:
  similarity_threshold: 0.70
  name_weight: 0.4
  type_weight: 0.2
  description_weight: 0.25
  source_weight: 0.15
```

### AI Output Structure

The AI pipeline generates several output files:

```
map_locations_ai/
├── temp/chunk_001.yaml          # Individual chunk results
├── temp/chunk_002.yaml
├── temp/merged.yaml             # Combined results
├── trace/trace_TIMESTAMP.json   # Individual LLM call traces
└── trace/run_TIMESTAMP.json     # Complete run summary
```

### AI Data Format

AI-extracted locations include additional fields:

```yaml
locations:
  - name: "Location Name"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
    description: "AI-generated description"
    source_text: "Exact text from input"
    confidence: 0.8
    is_url: false
    url: ""
    address: "Full address if available"
    extraction_method: "llm"
```

### AI Processing Examples

#### Extract from Travel Notes
```bash
# Process travel notes
python map_locations_ai/pipeline.py travel_notes.txt --config map_locations_ai/config.yaml

# Process with URL exploration
python map_locations_ai/pipeline.py travel_notes.txt --config map_locations_ai/config.yaml --with-urls

# Create map from extracted locations
map-locations map_locations_ai/temp/merged.yaml --output travel_map.html
```

#### Extract from Web Content
```bash
# Process content with URLs
python map_locations_ai/pipeline.py web_content.txt --config map_locations_ai/config.yaml --with-urls

# Process with deduplication
python map_locations_ai/pipeline.py web_content.txt --config map_locations_ai/config.yaml --deduplicate
```

#### Complete Workflow
```bash
# Extract, enhance, and deduplicate
python map_locations_ai/pipeline.py input.txt --config map_locations_ai/config.yaml --with-urls --deduplicate

# Create maps from results
map-locations map_locations_ai/temp/merged.yaml --output ai_extracted_map.html
map-locations map_locations_ai/temp/merged.yaml --format all --output exports/ai_locations
```

## Data Format

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
| `description` | string | ❌ | AI-generated description |
| `source_text` | string | ❌ | Exact text from AI extraction |
| `confidence` | float | ❌ | AI confidence score (0.1-0.9) |
| `is_url` | boolean | ❌ | Whether source is a URL |
| `url` | string | ❌ | Source URL if applicable |
| `address` | string | ❌ | Full address if available |
| `extraction_method` | string | ❌ | How location was extracted |

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
  description: "Historic covered passage with glass roof"
  source_text: "Passage du Grand Cerf - beautiful historic passage"
  confidence: 0.85
  is_url: false
  url: ""
  address: "145 rue Saint-Denis, 75002 Paris"
  extraction_method: "llm"
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

# Create mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html

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

# Mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html
```

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

## Mobile Optimization

The Map Locations library includes mobile-optimized features for better usability on smartphones and tablets.

### Mobile Features

#### Mobile-Optimized Layout
- **Collapsible Controls**: Filter panel can be toggled on/off with a button
- **Narrower Popups**: 300px width (vs 450px on desktop) for better mobile viewing
- **Touch-Friendly Interface**: Larger buttons and touch targets
- **Responsive Design**: Adapts to different screen sizes

#### Mobile-Specific Popup Content
- **Essential Information Only**: Streamlined popup content for mobile
- **Clickable Phone Numbers**: Tap to call phone numbers directly
- **Website Links**: Tap to open websites in new tabs
- **Truncated Descriptions**: Long descriptions are limited to 100 characters
- **Mobile Field Ordering**: Optimized field display order for mobile

#### Mobile Filtering Controls
- **Toggle Button**: Floating filter button in top-left corner
- **Collapsible Panel**: Filter panel can be shown/hidden
- **Compact Layout**: Smaller fonts and tighter spacing
- **Touch-Optimized**: Larger checkboxes and buttons

### Using Mobile Features

#### CLI Usage
```bash
# Create mobile-optimized map
map-locations locations.yaml --mobile --output mobile_map.html

# Mobile map with Google Maps tiles
map-locations locations.yaml --mobile --tile-provider google_maps --output mobile_google_map.html
```

#### Python Library Usage
```python
from map_locations import load_locations_from_yaml, show_locations_grouped

# Load locations
locations = load_locations_from_yaml("locations.yaml")

# Create mobile-optimized map
show_locations_grouped(
    locations,
    map_filename="mobile_map.html",
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

### Mobile Use Cases

#### Travel Planning
```bash
# Create mobile map for travel
map-locations travel_locations.yaml --mobile --output travel_mobile.html
```

#### Field Research
```bash
# Create mobile map for field work
map-locations research_locations.yaml --mobile --output research_mobile.html
```

#### Event Planning
```bash
# Create mobile map for events
map-locations event_locations.yaml --mobile --group-by type --output event_mobile.html
```

## Library Usage

### Basic Map Generation

```python
from map_locations import load_locations_from_yaml, show_locations_grouped

# Load locations from YAML
locations = load_locations_from_yaml("locations.yaml")

# Generate interactive map with grouping (defaults to type)
show_locations_grouped(locations, group_by="type", map_filename="map.html")

# Generate mobile-optimized map
show_locations_grouped(locations, group_by="type", map_filename="mobile_map.html", mobile=True)

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

# Mobile-optimized grouping
show_locations_grouped(locations, group_by="type", map_filename="mobile_type_map.html", mobile=True)
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

## Export Formats

### HTML Maps
Interactive web maps created with Folium that can be opened in any web browser.

**Features:**
- Interactive markers with popups
- Layer controls for grouping
- Zoom and pan navigation
- Multiple tile providers
- Mobile optimization support

### KML Export
KML files can be imported into Google My Maps and other mapping applications.

**Features:**
- Grouped folders for different location types
- Preserved metadata (tags, dates, descriptions)
- Compatible with Google My Maps
- Can be viewed in Google Earth

### GeoJSON Export
Standard geospatial format for use in GIS applications and web mapping.

**Features:**
- Standard geospatial format
- Compatible with most mapping libraries
- Preserves all location data
- Can be used in web applications

### JSON Export
Structured data export for programmatic use.

**Features:**
- Machine-readable format
- Preserves all location data
- Easy to parse and process
- Can be used for data analysis

### CSV Export
Spreadsheet-compatible format for data analysis.

**Features:**
- Opens in Excel, Google Sheets, etc.
- Easy to filter and sort
- Can be used for data analysis
- Human-readable format

## Map Features

### Interactive Elements

- **Clickable Markers**: Click on any location to see detailed popup with name, type, tags, and dates
- **Zoom Controls**: Zoom in/out with mouse wheel or controls
- **Pan Navigation**: Click and drag to move around the map
- **Fullscreen Mode**: Toggle fullscreen view
- **Layer Control**: Toggle visibility of different groups with the layer control panel
- **Mobile Optimization**: Collapsible controls and touch-friendly interface on mobile

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
- **Mobile Popups**: Streamlined content with clickable phone numbers and website links
- **Tooltips**: Hover over markers to see location names
- **Layer Control**: Toggle visibility of different groups using the layer control panel

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

## Google My Maps Integration

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

## Examples

### Paris Passages Map

The included example shows historic passages in Paris:

```bash
# Generate the Paris passages map grouped by type (default)
map-locations passages.yaml --group-by type --output passages_map.html

# Create mobile-optimized version
map-locations passages.yaml --group-by type --mobile --output passages_mobile.html
```

This creates an interactive map of Paris's historic covered passages with:
- Locations grouped by type (default)
- Color-coded groups with layer controls
- Detailed popups showing name, type, tags, and dates
- Interactive layer panel to toggle group visibility
- Mobile optimization for smartphones and tablets

### Custom Map with Google Satellite

```bash
# Create a satellite view map
map-locations locations.yaml --tile-provider google_satellite --output satellite_map.html

# Create mobile satellite view map
map-locations locations.yaml --tile-provider google_satellite --mobile --output mobile_satellite_map.html
```

### Export for Different Use Cases

```bash
# For Google My Maps
map-locations locations.yaml --format kml --output google_maps.kml

# For web applications
map-locations locations.yaml --format geojson --output web_app.geojson

# For data analysis
map-locations locations.yaml --format csv --output analysis.csv

# For all purposes
map-locations locations.yaml --format all --output complete_export/

# For mobile applications
map-locations locations.yaml --mobile --output mobile_app.html
```
