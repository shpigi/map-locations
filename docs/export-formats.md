# Export Formats

Complete guide to all export formats supported by Map Locations.

## Table of Contents

- [Overview](#overview)
- [HTML Maps](#html-maps)
- [KML Export](#kml-export)
- [GeoJSON Export](#geojson-export)
- [JSON Export](#json-export)
- [CSV Export](#csv-export)
- [CLI Usage](#cli-usage)
- [Library Usage](#library-usage)

## Overview

Map Locations supports multiple export formats for different use cases:

| Format | Use Case | Features |
|--------|----------|----------|
| **HTML** | Interactive web maps | Folium maps, layer controls, popups |
| **KML** | Google My Maps, Google Earth | Grouped folders, metadata preservation |
| **GeoJSON** | Web applications, GIS | Standard geospatial format |
| **JSON** | Data analysis, APIs | Machine-readable, structured data |
| **CSV** | Spreadsheets, analysis | Human-readable, Excel compatible |

## HTML Maps

Interactive web maps created with Folium that can be opened in any web browser.

### Features

- **Interactive Markers**: Click on any location to see detailed popup
- **Layer Controls**: Toggle visibility of different groups
- **Zoom and Pan**: Navigate around the map
- **Multiple Tile Providers**: OpenStreetMap, Google Maps, Google Satellite
- **Color Coding**: Different groups get distinct colors
- **Responsive Design**: Works on desktop and mobile

### CLI Usage

```bash
# Create basic HTML map
map-locations locations.yaml --output map.html

# Create map with Google Maps tiles
map-locations locations.yaml --tile-provider google_maps --output map.html

# Create map with Google Satellite view
map-locations locations.yaml --tile-provider google_satellite --output map.html

# Group by different fields
map-locations locations.yaml --group-by neighborhood --output map.html
```

### Library Usage

```python
from map_locations import show_locations_grouped

# Basic map
show_locations_grouped(locations, map_filename="map.html")

# Map with Google Maps tiles
show_locations_grouped(
    locations,
    group_by="type",
    map_filename="google_maps.html",
    tile_provider="google_maps"
)

# Map with custom grouping
show_locations_grouped(
    locations,
    group_by="neighborhood",
    map_filename="neighborhood_map.html"
)
```

### HTML Map Features

#### Interactive Elements

- **Clickable Markers**: Click any marker to see detailed information
- **Zoom Controls**: Use mouse wheel or zoom buttons
- **Pan Navigation**: Click and drag to move around
- **Fullscreen Mode**: Toggle fullscreen view
- **Layer Control**: Toggle visibility of different groups

#### Popup Information

Each marker shows:
- Location name
- Type/category
- Tags (if any)
- Date added (if any)
- Date of visit (if any)

#### Color Coding

- Each group gets a unique color
- Colors cycle through a predefined palette
- Gray is used for additional groups beyond the palette

## KML Export

KML (Keyhole Markup Language) files can be imported into Google My Maps, Google Earth, and other mapping applications.

### Features

- **Grouped Folders**: Different location types are organized in separate folders
- **Metadata Preservation**: All location data is preserved
- **Google My Maps Compatible**: Perfect for importing into Google My Maps
- **Google Earth Compatible**: Can be viewed in Google Earth
- **Rich Descriptions**: Popup information is included in descriptions

### CLI Usage

```bash
# Export to KML
map-locations locations.yaml --format kml --output locations.kml

# Export to KML with custom filename
map-locations locations.yaml --format kml --output my_trip.kml
```

### Library Usage

```python
from map_locations import export_to_kml

# Export to KML
kml_file = export_to_kml(locations, "locations.kml")
print(f"Exported to {kml_file}")
```

### Google My Maps Integration

1. **Export to KML**:
   ```bash
   map-locations locations.yaml --format kml --output my_locations.kml
   ```

2. **Import to Google My Maps**:
   - Go to [Google My Maps](https://www.google.com/maps/d/u/0/)
   - Click "Create a new map"
   - Click "Import" in the left panel
   - Upload your KML file
   - Your locations will appear with all details preserved

### Google My Maps Features

- 📱 **Mobile Access**: View maps on smartphones and tablets
- 👥 **Sharing**: Share maps via link or email
- 🎨 **Custom Styling**: Change colors, icons, and labels
- 📝 **Collaboration**: Allow others to edit your maps
- 🗺️ **Offline Access**: Download maps for offline use
- 📍 **Custom Markers**: Add custom icons and descriptions
- 🗂️ **Layers**: Organize locations into different layers

## GeoJSON Export

Standard geospatial format for use in GIS applications and web mapping.

### Features

- **Standard Format**: Widely supported by mapping libraries
- **Web Compatible**: Perfect for web applications
- **GIS Compatible**: Works with QGIS, ArcGIS, etc.
- **Metadata Preservation**: All location data is preserved
- **Lightweight**: Efficient for web applications

### CLI Usage

```bash
# Export to GeoJSON
map-locations locations.yaml --format geojson --output locations.geojson

# Export to GeoJSON with custom filename
map-locations locations.yaml --format geojson --output web_app.geojson
```

### Library Usage

```python
from map_locations import export_to_geojson

# Export to GeoJSON
geojson_file = export_to_geojson(locations, "locations.geojson")
print(f"Exported to {geojson_file}")
```

### Web Application Usage

```javascript
// Load GeoJSON in a web application
fetch('locations.geojson')
  .then(response => response.json())
  .then(data => {
    // Add to map
    map.addSource('locations', {
      type: 'geojson',
      data: data
    });
  });
```

## JSON Export

Structured data export for programmatic use and data analysis.

### Features

- **Machine Readable**: Easy to parse and process
- **Structured Data**: Preserves all location information
- **API Compatible**: Perfect for web APIs
- **Data Analysis**: Can be used for statistical analysis
- **Cross Platform**: Works with any programming language

### CLI Usage

```bash
# Export to JSON
map-locations locations.yaml --format json --output locations.json

# Export to JSON with custom filename
map-locations locations.yaml --format json --output api_data.json
```

### Library Usage

```python
from map_locations import export_to_json

# Export to JSON
json_file = export_to_json(locations, "locations.json")
print(f"Exported to {json_file}")
```

### JSON Structure

```json
{
  "locations": [
    {
      "name": "Eiffel Tower",
      "type": "landmark",
      "latitude": 48.8584,
      "longitude": 2.2945,
      "tags": ["historic", "tourist"],
      "neighborhood": "7th arrondissement",
      "date_added": "2025-01-15",
      "date_of_visit": "2025-01-20"
    }
  ]
}
```

### Data Analysis Example

```python
import json
import pandas as pd

# Load JSON data
with open('locations.json', 'r') as f:
    data = json.load(f)

# Convert to pandas DataFrame
df = pd.DataFrame(data['locations'])

# Analyze data
print(f"Total locations: {len(df)}")
print(f"Types: {df['type'].unique()}")
print(f"Average latitude: {df['latitude'].mean()}")
```

## CSV Export

Spreadsheet-compatible format for data analysis and human review.

### Features

- **Excel Compatible**: Opens in Excel, Google Sheets, etc.
- **Human Readable**: Easy to review and edit
- **Data Analysis**: Perfect for statistical analysis
- **Filtering**: Easy to filter and sort in spreadsheets
- **Universal Format**: Works with any spreadsheet application

### CLI Usage

```bash
# Export to CSV
map-locations locations.yaml --format csv --output locations.csv

# Export to CSV with custom filename
map-locations locations.yaml --format csv --output analysis.csv
```

### Library Usage

```python
from map_locations import export_to_csv

# Export to CSV
csv_file = export_to_csv(locations, "locations.csv")
print(f"Exported to {csv_file}")
```

### CSV Structure

```csv
name,type,latitude,longitude,tags,neighborhood,date_added,date_of_visit
Eiffel Tower,landmark,48.8584,2.2945,"historic,tourist",7th arrondissement,2025-01-15,2025-01-20
Central Park,park,40.7829,-73.9654,"outdoor,recreation",Upper East Side,2025-01-10,2025-01-25
```

### Spreadsheet Analysis

1. **Open in Excel/Google Sheets**
2. **Filter by type**: Select the type column and filter
3. **Sort by date**: Sort by date_added or date_of_visit
4. **Create pivot tables**: Analyze by type, neighborhood, etc.
5. **Create charts**: Visualize your data

## CLI Usage

### Basic Export Commands

```bash
# Export to specific format
map-locations locations.yaml --format html --output map.html
map-locations locations.yaml --format kml --output locations.kml
map-locations locations.yaml --format geojson --output locations.geojson
map-locations locations.yaml --format json --output locations.json
map-locations locations.yaml --format csv --output locations.csv

# Export to all formats
map-locations locations.yaml --format all --output exports/locations
```

### Advanced Export Options

```bash
# Export with custom grouping
map-locations locations.yaml --format kml --group-by neighborhood --output neighborhoods.kml

# Export with different tile providers (for HTML)
map-locations locations.yaml --format html --tile-provider google_maps --output google_map.html
map-locations locations.yaml --format html --tile-provider google_satellite --output satellite_map.html
```

### Export Examples

```bash
# For Google My Maps
map-locations trip.yaml --format kml --output google_maps.kml

# For web applications
map-locations data.yaml --format geojson --output web_app.geojson

# For data analysis
map-locations data.yaml --format csv --output analysis.csv

# For APIs
map-locations data.yaml --format json --output api_data.json

# For all purposes
map-locations data.yaml --format all --output complete_export/
```

## Library Usage

### Export Functions

```python
from map_locations import (
    export_to_html,
    export_to_kml,
    export_to_geojson,
    export_to_json,
    export_to_csv,
    export_to_all_formats
)

# Export to specific format
html_file = export_to_html(locations, "map.html")
kml_file = export_to_kml(locations, "locations.kml")
geojson_file = export_to_geojson(locations, "locations.geojson")
json_file = export_to_json(locations, "locations.json")
csv_file = export_to_csv(locations, "locations.csv")

# Export to all formats
files = export_to_all_formats(locations, "exports/my_locations")
print(f"Exported {len(files)} files")
```

### Batch Processing

```python
def export_for_different_use_cases(locations):
    """Export locations for different use cases."""

    # For Google My Maps
    kml_file = export_to_kml(locations, "google_maps.kml")

    # For web applications
    geojson_file = export_to_geojson(locations, "web_app.geojson")

    # For data analysis
    csv_file = export_to_csv(locations, "analysis.csv")

    # For APIs
    json_file = export_to_json(locations, "api_data.json")

    return {
        "google_maps": kml_file,
        "web_app": geojson_file,
        "analysis": csv_file,
        "api": json_file
    }
```

### Conditional Export

```python
def smart_export(locations, use_case):
    """Export based on use case."""

    if use_case == "google_maps":
        return export_to_kml(locations, "locations.kml")

    elif use_case == "web_app":
        return export_to_geojson(locations, "locations.geojson")

    elif use_case == "analysis":
        return export_to_csv(locations, "locations.csv")

    elif use_case == "api":
        return export_to_json(locations, "locations.json")

    else:
        # Default to all formats
        return export_to_all_formats(locations, "exports/locations")
```

## File Size Considerations

### Typical File Sizes

| Format | Size per 100 locations | Notes |
|--------|------------------------|-------|
| **HTML** | 50-200 KB | Depends on map complexity |
| **KML** | 10-50 KB | Efficient for metadata |
| **GeoJSON** | 5-20 KB | Lightweight geospatial format |
| **JSON** | 5-15 KB | Compact structured data |
| **CSV** | 3-10 KB | Most compact format |

### Optimization Tips

1. **Use specific formats** rather than all formats when possible
2. **Filter data** before exporting large datasets
3. **Compress files** for web delivery (gzip)
4. **Consider clustering** for very large datasets (>1000 locations)

## Best Practices

### 1. Choose the Right Format

```bash
# For interactive viewing
map-locations data.yaml --format html --output map.html

# For Google My Maps
map-locations data.yaml --format kml --output google_maps.kml

# For web applications
map-locations data.yaml --format geojson --output web_app.geojson

# For data analysis
map-locations data.yaml --format csv --output analysis.csv

# For APIs
map-locations data.yaml --format json --output api_data.json
```

### 2. Use Descriptive Filenames

```bash
# Good
map-locations paris_trip.yaml --format kml --output paris_trip.kml
map-locations restaurants.yaml --format csv --output restaurant_analysis.csv

# Avoid
map-locations data.yaml --format kml --output data.kml
map-locations data.yaml --format csv --output data.csv
```

### 3. Organize Output Files

```bash
# Create organized directory structure
mkdir -p exports/{maps,data,analysis}

# Export to organized locations
map-locations trip.yaml --format html --output exports/maps/trip_map.html
map-locations trip.yaml --format kml --output exports/maps/trip.kml
map-locations trip.yaml --format csv --output exports/analysis/trip_data.csv
map-locations trip.yaml --format json --output exports/data/trip_api.json
```

### 4. Version Control

```bash
# Include date in filename
map-locations data.yaml --format all --output exports/locations_$(date +%Y%m%d)

# Include version in filename
map-locations data.yaml --format all --output exports/locations_v1.0
```
