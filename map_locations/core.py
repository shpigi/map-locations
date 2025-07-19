import folium
import yaml
import json
import csv
from collections import defaultdict
from pathlib import Path
import os

def load_locations_from_yaml(yaml_path):
    """
    Load locations from a YAML file with the expected structure.
    """
    with open(yaml_path, 'r') as f:
        data = yaml.safe_load(f)
    return data.get("locations", [])


def export_to_json(locations, output_path):
    """
    Export locations to JSON format.
    
    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({"locations": locations}, f, indent=2, ensure_ascii=False)
    
    print(f"📄 JSON exported to: {Path(output_path).resolve()}")


def export_to_csv(locations, output_path):
    """
    Export locations to CSV format.
    
    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the CSV file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    if not locations:
        return
    
    # Get all possible fields from all locations
    all_fields = set()
    for loc in locations:
        all_fields.update(loc.keys())
    
    fieldnames = sorted(list(all_fields))
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for loc in locations:
            # Ensure all fields are present (fill missing with empty string)
            row = {field: loc.get(field, '') for field in fieldnames}
            # Handle tags as comma-separated string
            if 'tags' in row and isinstance(row['tags'], list):
                row['tags'] = ', '.join(row['tags'])
            writer.writerow(row)
    
    print(f"📊 CSV exported to: {Path(output_path).resolve()}")


def export_to_geojson(locations, output_path):
    """
    Export locations to GeoJSON format.
    
    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the GeoJSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for loc in locations:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc['longitude'], loc['latitude']]
            },
            "properties": {
                "name": loc['name'],
                "type": loc.get('type', ''),
                "tags": loc.get('tags', []),
                "neighborhood": loc.get('neighborhood', ''),
                "date_added": loc.get('date_added', ''),
                "date_visited": loc.get('date_visited', '')
            }
        }
        geojson["features"].append(feature)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)
    
    print(f"🗺️ GeoJSON exported to: {Path(output_path).resolve()}")


def export_to_kml(locations, output_path):
    """
    Export locations to KML format.
    
    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the KML file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Locations</name>
    <description>Exported locations</description>
'''
    
    for loc in locations:
        tags_str = ', '.join(loc.get('tags', [])) if loc.get('tags') else ''
        description = f"Type: {loc.get('type', '')}<br>Tags: {tags_str}<br>Neighborhood: {loc.get('neighborhood', '')}<br>Date Added: {loc.get('date_added', '')}<br>Date Visited: {loc.get('date_visited', '')}"
        
        kml_content += f'''    <Placemark>
      <name>{loc['name']}</name>
      <description><![CDATA[{description}]]></description>
      <Point>
        <coordinates>{loc['longitude']},{loc['latitude']},0</coordinates>
      </Point>
    </Placemark>
'''
    
    kml_content += '''  </Document>
</kml>'''
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(kml_content)
    
    print(f"🗺️ KML exported to: {Path(output_path).resolve()}")


def export_to_all_formats(locations, base_path):
    """
    Export locations to all supported formats.
    
    Args:
        locations (list): List of location dictionaries
        base_path (str): Base path for output files (without extension)
    """
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    
    # Export to different formats
    export_to_json(locations, f"{base_path}.json")
    export_to_csv(locations, f"{base_path}.csv")
    export_to_geojson(locations, f"{base_path}.geojson")
    export_to_kml(locations, f"{base_path}.kml")
    
    print(f"✅ All formats exported to: {Path(base_path).parent}")


def show_locations_grouped(locations, group_by="neighborhood", map_filename="map.html"):
    """
    Create a folium map showing locations grouped by a specified field.
    
    Args:
        locations (list): List of dicts loaded from YAML.
        group_by (str): Field to group markers by (e.g., neighborhood, date_added).
        map_filename (str): Path to save the HTML map.
    """
    if not locations:
        raise ValueError("No locations provided.")

    # Center the map
    first = locations[0]
    m = folium.Map(location=[first['latitude'], first['longitude']], zoom_start=14)

    # Group locations
    groups = defaultdict(list)
    for loc in locations:
        key = loc.get(group_by, "Unknown")
        groups[key].append(loc)

    # Color cycle
    colors = [
        "red", "blue", "green", "purple", "orange", "darkred",
        "lightred", "beige", "darkblue", "darkgreen", "cadetblue"
    ]
    color_cycle = iter(colors)

    for group_name, group_locs in groups.items():
        fg = folium.FeatureGroup(name=f"{group_by.capitalize()}: {group_name}")
        color = next(color_cycle, "gray")

        for loc in group_locs:
            popup_html = f"""
            <b>{loc['name']}</b><br>
            Type: {loc.get('type', '')}<br>
            Tags: {', '.join(loc.get('tags', []))}<br>
            Date added: {loc.get('date_added', '')}<br>
            Date visited: {loc.get('date_visited', '')}
            """
            folium.Marker(
                location=[loc['latitude'], loc['longitude']],
                popup=popup_html,
                tooltip=loc['name'],
                icon=folium.Icon(color=color)
            ).add_to(fg)

        fg.add_to(m)

    folium.LayerControl(collapsed=False).add_to(m)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(map_filename), exist_ok=True)
    
    m.save(map_filename)
    print(f"🗺️ Map saved to: {Path(map_filename).resolve()}")


# ✅ Run this to test
if __name__ == "__main__":
    yaml_path = "passages.yaml"  # Replace with your actual YAML file path
    locations = load_locations_from_yaml(yaml_path)
    
    # Create interactive map
    show_locations_grouped(locations, group_by="neighborhood", map_filename="./maps/passages/map.html")
    
    # Export to all formats
    export_to_all_formats(locations, "./maps/passages/passages")
