import csv
import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, cast

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
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
    Export locations to KML format with separate folders for each location type.

    Args:
        locations (list): List of location dictionaries
        output_path (str): Path to save the KML file
    """
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Define color and icon mapping for different location types
    type_styles = {
        # Food & Drink (Red)
        "restaurant": {
            "color": "ff0000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        },
        "cafe": {
            "color": "ff0000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        },
        "bar": {
            "color": "ff0000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        },
        # Culture & Arts (Light Blue)
        "museum": {
            "color": "ff00ffff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png",
        },
        "gallery": {
            "color": "ff00ffff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png",
        },
        "theater": {
            "color": "ff00ffff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png",
        },
        "theatre": {
            "color": "ff00ffff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png",
        },
        # Nature & Outdoors (Green)
        "park": {
            "color": "ff00ff00",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png",
        },
        "garden": {
            "color": "ff00ff00",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png",
        },
        # Shopping & Commerce (Blue)
        "shopping": {
            "color": "ffff0000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
        },
        "store": {
            "color": "ffff0000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
        },
        "market": {
            "color": "ffff0000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
        },
        # Accommodation (Yellow)
        "hotel": {
            "color": "ffffff00",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
        },
        "accommodation": {
            "color": "ffffff00",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
        },
        # Transport (Gray)
        "transport": {
            "color": "ff808080",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png",
        },
        "station": {
            "color": "ff808080",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png",
        },
        # Landmarks & Monuments (Orange)
        "landmark": {
            "color": "ffff8000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
        },
        "monument": {
            "color": "ffff8000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
        },
        "church": {
            "color": "ffff8000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
        },
        "temple": {
            "color": "ffff8000",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
        },
        # Entertainment & Experiences (Purple)
        "cinema": {
            "color": "ff8000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
        },
        "entertainment": {
            "color": "ff8000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
        },
        "theme_park": {
            "color": "ff8000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
        },
        "experience": {
            "color": "ff8000ff",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
        },
        # Neighborhoods & Areas (Brown)
        "neighborhood": {
            "color": "ff8b4513",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
        },
        # Bridges (Gray)
        "bridge": {
            "color": "ff808080",
            "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png",
        },
    }

    # Default style for unknown types
    default_style = {
        "color": "ff808080",
        "icon": "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png",
    }

    # Group locations by type
    from collections import defaultdict

    grouped_locations = defaultdict(list)
    for loc in locations:
        loc_type = loc.get("type", "").lower()
        grouped_locations[loc_type].append(loc)

    kml_content = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
        "  <Document>\n"
        "    <name>Map Locations</name>\n"
        "    <description>Exported locations grouped by type</description>\n"
    )

    # Add styles for each location type
    for loc_type, style in type_styles.items():
        style_id = f"style_{loc_type}"
        kml_content += (
            f'    <Style id="{style_id}">\n'
            f"      <IconStyle>\n"
            f"        <color>{style['color']}</color>\n"
            f"        <scale>1.0</scale>\n"
            f"        <Icon>\n"
            f"          <href>{style['icon']}</href>\n"
            f"        </Icon>\n"
            f"      </IconStyle>\n"
            f"      <LabelStyle>\n"
            f"        <color>{style['color']}</color>\n"
            f"        <scale>0.8</scale>\n"
            f"      </LabelStyle>\n"
            f"    </Style>\n"
        )

    # Add default style
    kml_content += (
        f'    <Style id="style_default">\n'
        f"      <IconStyle>\n"
        f"        <color>{default_style['color']}</color>\n"
        f"        <scale>1.0</scale>\n"
        f"        <Icon>\n"
        f"          <href>{default_style['icon']}</href>\n"
        f"        </Icon>\n"
        f"      </IconStyle>\n"
        f"      <LabelStyle>\n"
        f"        <color>{default_style['color']}</color>\n"
        f"        <scale>0.8</scale>\n"
        f"      </LabelStyle>\n"
        f"    </Style>\n"
    )

    # Create folders for each location type
    for loc_type, type_locations in grouped_locations.items():
        # Get style for this type
        style = type_styles.get(loc_type, default_style)
        style_id = f"#style_{loc_type}" if loc_type in type_styles else "#style_default"

        # Create folder name with count
        folder_name = f"📍 {loc_type.title()} ({len(type_locations)} locations)"

        kml_content += (
            f"    <Folder>\n"
            f"      <name>{folder_name}</name>\n"
            f"      <description>Locations of type: {loc_type}</description>\n"
        )

        # Add placemarks for this type
        for loc in type_locations:
            tags_str = ", ".join(loc.get("tags", [])) if loc.get("tags", []) else ""
            neighborhood = loc.get("neighborhood", "") or "Not specified"
            date_added = loc.get("date_added", "") or "Not specified"
            date_of_visit = loc.get("date_of_visit", "") or "Not specified"

            description = (
                f"<![CDATA["
                f'<div style="font-family: Arial, sans-serif; max-width: 300px;">'
                f"<h3 style=\"color: #333; margin: 0 0 10px 0;\">{loc['name']}</h3>"
                f'<p style="margin: 5px 0;"><strong>Type:</strong> '
                f"{loc.get('type', 'Not specified')}</p>"
                f'<p style="margin: 5px 0;"><strong>Tags:</strong> {tags_str}</p>'
                f'<p style="margin: 5px 0;"><strong>Neighborhood:</strong> '
                f"{neighborhood}</p>"
                f'<p style="margin: 5px 0;"><strong>Date Added:</strong> '
                f"{date_added}</p>"
                f'<p style="margin: 5px 0;"><strong>Date of Visit:</strong> '
                f"{date_of_visit}</p>"
                f"</div>"
                f"]]>"
            )

            placemark = (
                f"      <Placemark>\n"
                f"        <name>{loc['name']}</name>\n"
                f"        <description>{description}</description>\n"
                f"        <styleUrl>{style_id}</styleUrl>\n"
                f"        <Point>\n"
                f"          <coordinates>{loc['longitude']}, {loc['latitude']}, 0</coordinates>\n"
                f"        </Point>\n"
                f"      </Placemark>\n"
            )
            kml_content += placemark

        kml_content += "    </Folder>\n"

    kml_content += "  </Document>\n</kml>\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(kml_content)

    print(f"🗺️ KML exported to: {Path(output_path).resolve()}")
    print(f"📋 Created {len(grouped_locations)} separate groups in KML:")
    for loc_type, type_locations in grouped_locations.items():
        print(f"   • {loc_type.title()} ({len(type_locations)} locations)")


def export_to_all_formats(locations: List[Dict[str, Any]], base_path: str) -> None:
    """
    Export locations to all supported formats.

    Args:
        locations (list): List of location dictionaries
        base_path (str): Base path for output files (without extension)
    """
    # Create directory if needed
    output_dir = os.path.dirname(base_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Export to different formats
    export_to_json(locations, f"{base_path}.json")
    export_to_csv(locations, f"{base_path}.csv")
    export_to_geojson(locations, f"{base_path}.geojson")
    export_to_kml(locations, f"{base_path}.kml")

    # Show output location
    if output_dir:
        print(f"✅ Data formats exported to: {Path(output_dir).resolve()}")
    else:
        print(f"✅ Data formats exported to: {Path.cwd()}")


def get_type_color(loc_type: str) -> str:
    """
    Get the appropriate color for a location type, matching the KML color scheme.

    Args:
        loc_type (str): The location type

    Returns:
        str: The color name for folium
    """
    # Type to color mapping matching KML export (using valid folium colors)
    type_colors = {
        # Food & Drink (Red)
        "restaurant": "red",
        "cafe": "red",
        "bar": "red",
        # Culture & Arts (Cadet Blue)
        "museum": "cadetblue",
        "gallery": "cadetblue",
        "theater": "cadetblue",
        "theatre": "cadetblue",
        # Nature & Outdoors (Green)
        "park": "green",
        "garden": "green",
        # Shopping & Commerce (Blue)
        "shopping": "blue",
        "store": "blue",
        "market": "blue",
        # Accommodation (Yellow)
        "hotel": "yellow",
        "accommodation": "yellow",
        # Transport (Gray)
        "transport": "gray",
        "station": "gray",
        # Landmarks & Monuments (Orange)
        "landmark": "orange",
        "monument": "orange",
        "church": "orange",
        "temple": "orange",
        # Entertainment & Experiences (Purple)
        "cinema": "purple",
        "entertainment": "purple",
        "theme_park": "purple",
        "experience": "purple",
        # Neighborhoods & Areas (Dark Red)
        "neighborhood": "darkred",
    }

    return type_colors.get(loc_type.lower(), "gray")


def show_locations_grouped(
    locations: List[Dict[str, Any]],
    group_by: str = "type",
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
    filter_types: Optional[List[str]] = None,
) -> None:
    """
    Create a folium map showing locations grouped by a specified field.

    Args:
        locations (list): List of dicts loaded from YAML.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added).
        map_filename (str): Path to save the HTML map.
        tile_provider (str): Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        filter_types (list, optional): List of location types to include.
    """
    if not locations:
        raise ValueError("No locations provided.")

    # Filter locations by type if filter_types is provided
    if filter_types:
        locations = [
            loc
            for loc in locations
            if loc.get("type", "").lower() in [t.lower() for t in filter_types]
        ]
        if not locations:
            raise ValueError(f"No locations found matching the specified types: {filter_types}")

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

    # Create feature groups with better naming
    feature_groups = {}
    for group_name, group_locs in groups.items():
        # Create a more descriptive group name
        if group_by == "type":
            group_display_name = f"📍 {group_name.title()} ({len(group_locs)} locations)"
        elif group_by == "neighborhood":
            group_display_name = f"🏘️ {group_name} ({len(group_locs)} locations)"
        elif group_by == "date_added":
            group_display_name = f"📅 Added: {group_name} ({len(group_locs)} locations)"
        elif group_by == "date_of_visit":
            group_display_name = f"🎯 Visited: {group_name} ({len(group_locs)} locations)"
        else:
            group_display_name = f"{group_by.title()}: {group_name} ({len(group_locs)} locations)"

        fg = folium.FeatureGroup(name=group_display_name)
        feature_groups[group_name] = fg

        for loc in group_locs:
            # Get color based on location type
            color = get_type_color(loc.get("type", ""))

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

    # Add layer control with better positioning and styling
    folium.LayerControl(
        position="topright",
        collapsed=False,
        autoZIndex=True,
        overlay=True,
        control=True,
    ).add_to(m)

    # Create output directory if needed
    dirname = os.path.dirname(map_filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    m.save(map_filename)
    print(f"🗺️ Map saved to: {Path(map_filename).resolve()}")
    print(f"📋 Created {len(feature_groups)} separate groups that can be toggled on/off:")
    for group_name, fg in feature_groups.items():
        print(f"   • {group_name.title()} ({len(groups[group_name])} locations)")


def show_locations_with_filtering(
    locations: List[Dict[str, Any]],
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
    filter_types: Optional[List[str]] = None,
    group_by: str = "type",
) -> None:
    """
    Create a folium map with filtering capabilities for location types.

    Args:
        locations (list): List of dicts loaded from YAML.
        map_filename (str): Path to save the HTML map.
        tile_provider (str): Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        filter_types (list, optional): List of location types to include.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added).
    """
    show_locations_grouped(
        locations=locations,
        group_by=group_by,
        map_filename=map_filename,
        tile_provider=tile_provider,
        filter_types=filter_types,
    )


def get_available_types(locations: List[Dict[str, Any]]) -> List[str]:
    """
    Get a list of all available location types from the locations data.

    Args:
        locations (list): List of location dictionaries

    Returns:
        list: List of unique location types
    """
    types = set()
    for loc in locations:
        loc_type = loc.get("type", "")
        if loc_type:
            types.add(loc_type.lower())
    return sorted(list(types))


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
