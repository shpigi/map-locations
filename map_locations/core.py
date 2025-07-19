import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Sequence, Set, Union, cast

import folium
import yaml


def load_locations_from_yaml(yaml_path: str) -> List[Dict[str, Any]]:
    """
    Load locations from a YAML file with the expected structure.
    """
    with open(yaml_path, "r") as f:
        data = cast(Dict[str, Any], yaml.safe_load(f))
    return cast(List[Dict[str, Any]], data.get("locations", []))


def export_to_json(locations: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export locations to JSON format.

    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"locations": locations}, f, indent=2, ensure_ascii=False)

    print(f"📄 JSON exported to: {Path(output_path).resolve()}")


def export_to_csv(locations: List[Dict[str, Any]], output_path: str) -> None:
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
    all_fields: Set[str] = set()
    for loc in locations:
        all_fields.update(loc.keys())

    fieldnames = sorted(list(all_fields))

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for loc in locations:
            # Ensure all fields are present (fill missing with empty string)
            row = {field: loc.get(field, "") for field in fieldnames}
            # Handle tags as comma-separated string
            if "tags" in row and isinstance(row["tags"], list):
                row["tags"] = ", ".join(row["tags"])
            writer.writerow(row)

    print(f"📊 CSV exported to: {Path(output_path).resolve()}")


def export_to_geojson(locations: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export locations to GeoJSON format.

    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the GeoJSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    geojson: Dict[str, Any] = {"type": "FeatureCollection", "features": []}

    for loc in locations:
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [loc["longitude"], loc["latitude"]],
            },
            "properties": {
                "name": loc["name"],
                "type": loc.get("type", ""),
                "tags": loc.get("tags", []),
                "neighborhood": loc.get("neighborhood", ""),
                "date_added": loc.get("date_added", ""),
                "date_of_visit": loc.get("date_of_visit", ""),
            },
        }
        geojson["features"].append(feature)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"🗺️ GeoJSON exported to: {Path(output_path).resolve()}")


def export_to_kml(locations: List[Dict[str, Any]], output_path: str) -> None:
    """
    Export locations to KML format.

    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the KML file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    kml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "  <Document>\n"
        "    <name>Locations</name>\n"
        "    <description>Exported locations</description>\n"
    )

    for loc in locations:
        tags_str = ", ".join(loc.get("tags", [])) if loc.get("tags") else ""
        neighborhood = loc.get("neighborhood", "") or "Not specified"
        date_added = loc.get("date_added", "") or "Not specified"
        date_of_visit = loc.get("date_of_visit", "") or "Not specified"
        description = (
            f"Type: {loc.get('type', 'Not specified')}<br>"
            f"Tags: {tags_str}<br>"
            f"Neighborhood: {neighborhood}<br>"
            f"Date Added: {date_added}<br>"
            f"Date of Visit: {date_of_visit}"
        )
        placemark = (
            f"<Placemark>\n"
            f"<name>{loc['name']}</name>\n"
            f"<description><![CDATA[{description}]]></description>\n"
            f"<Point>\n"
            f"<coordinates>{loc['longitude']}, {loc['latitude']}, 0</coordinates>\n"
            f"</Point>\n"
            f"</Placemark>\n"
        )
        kml_content += placemark

    kml_content += "  </Document>\n</kml>\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"🗺️ KML exported to: {Path(output_path).resolve()}")


def export_to_all_formats(locations: List[Dict[str, Any]], base_path: str) -> None:
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


def show_locations_grouped(
    locations: List[Dict[str, Any]],
    group_by: str = "type",
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
) -> None:
    """
    Create a folium map showing locations grouped by a specified field.

    Args:
        locations (list): List of dicts loaded from YAML.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added).
        map_filename (str): Path to save the HTML map.
        tile_provider (str): Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
    """
    if not locations:
        raise ValueError("No locations provided.")

    # Center the map
    first = locations[0]
    m = folium.Map(location=[first["latitude"], first["longitude"]], zoom_start=14)

    # Add tile layer based on provider
    if tile_provider == "google_maps":
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="Google Maps",
            name="Google Maps",
        ).add_to(m)
    elif tile_provider == "google_satellite":
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite",
            name="Google Satellite",
        ).add_to(m)
    else:  # Default to OpenStreetMap
        folium.TileLayer(tiles="OpenStreetMap", name="OpenStreetMap").add_to(m)

    # Group locations
    groups = defaultdict(list)
    for loc in locations:
        key = loc.get(group_by, "Unknown")
        groups[key].append(loc)

    # Color cycle
    colors = [
        "red",
        "blue",
        "green",
        "purple",
        "orange",
        "darkred",
        "lightred",
        "beige",
        "darkblue",
        "darkgreen",
        "cadetblue",
    ]
    color_cycle = iter(colors)

    for group_name, group_locs in groups.items():
        fg = folium.FeatureGroup(name=f"{group_by.capitalize()}: {group_name}")
        color = next(color_cycle, "gray")
        for loc in group_locs:
            # Create popup content with better styling
            tags_str = ", ".join(loc.get("tags", [])) if loc.get("tags") else "None"
            neighborhood = loc.get("neighborhood", "") or "Not specified"
            date_added = loc.get("date_added", "") or "Not specified"
            date_of_visit = loc.get("date_of_visit", "") or "Not specified"

            # Create popup with better structure and width
            popup_html = (
                f"<div><h4>{loc['name']}</h4>"
                f"<p><strong>Type: </strong>{loc.get('type', 'Not specified')}</p>"
                f"<p><strong>Tags: </strong>{tags_str}</p>"
                f"<p><strong>Neighborhood: </strong>{neighborhood}</p>"
                f"<p><strong>Date Added: </strong>{date_added}</p>"
                f"<p><strong>Date of Visit: </strong>{date_of_visit}</p></div>"
            )

            folium.Marker(
                location=[loc["latitude"], loc["longitude"]],
                popup=folium.Popup(popup_html, max_width=450),
                tooltip=loc["name"],
                icon=folium.Icon(color=color),
            ).add_to(fg)
        fg.add_to(m)
    folium.LayerControl(collapsed=False).add_to(m)
    dirname = os.path.dirname(map_filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    m.save(map_filename)
    print(f"🗺️ Map saved to: {Path(map_filename).resolve()}")


def show_locations_with_google_maps(
    locations: List[Dict[str, Any]],
    group_by: str = "type",
    map_filename: str = "map.html",
    satellite: bool = False,
) -> None:
    """
    Create a folium map with Google Maps tiles showing locations grouped by a specified field.

    Note: This uses Google Maps tiles which are free for personal use but may require
    an API key for commercial use or high volume usage.

    Args:
        locations (list): List of dicts loaded from YAML.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added).
        map_filename (str): Path to save the HTML map.
        satellite (bool): Use satellite view instead of street view
    """
    tile_provider = "google_satellite" if satellite else "google_maps"
    show_locations_grouped(locations, group_by, map_filename, tile_provider)


# ✅ Run this to test
if __name__ == "__main__":
    yaml_path = "paris_london_trip_locations.yaml"  # Replace with your actual YAML file path
    locations = load_locations_from_yaml(yaml_path)

    # Create interactive map
    show_locations_grouped(
        locations, group_by="type", map_filename="./maps/paris_london_trip/map.html"
    )

    # Export to all formats
    export_to_all_formats(locations, "./maps/paris_london_trip/export")
