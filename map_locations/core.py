import csv
import json
import os
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, TypedDict, Union, cast

import folium
import yaml


class Location(TypedDict, total=False):
    """Type definition for a location entry.

    Attributes:
        name: The name of the location (required)
        type: The type/category of the location (required)
        latitude: Latitude coordinate (required)
        longitude: Longitude coordinate (required)
        tags: List of tags for filtering (optional)
        neighborhood: Neighborhood or area name (optional)
        date_added: Date when location was added (optional)
        date_of_visit: Date when location was visited (optional)
    """

    name: str
    type: str
    latitude: float
    longitude: float
    tags: List[str]
    neighborhood: str
    date_added: str
    date_of_visit: str


def load_locations_from_yaml(yaml_path: str) -> List[Location]:
    """
    Load locations from a YAML file with the expected structure.

    Args:
        yaml_path: Path to the YAML file containing location data

    Returns:
        List of location dictionaries with standardized structure

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is malformed

    Example:
        >>> locations = load_locations_from_yaml("my_locations.yaml")
        >>> print(f"Loaded {len(locations)} locations")
    """
    with open(yaml_path, "r") as f:
        data = cast(Dict[str, Any], yaml.safe_load(f))
    return cast(List[Location], data.get("locations", []))


def export_to_json(locations: List[Location], output_path: str) -> None:
    """
    Export locations to JSON format.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the JSON file

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> export_to_json(locations, "output.json")
    """
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"locations": locations}, f, indent=2, ensure_ascii=False)

    print(f"📄 JSON exported to: {Path(output_path).resolve()}")


def export_to_csv(locations: List[Location], output_path: str) -> None:
    """
    Export locations to CSV format.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the CSV file

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> export_to_csv(locations, "output.csv")
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


def export_to_geojson(locations: List[Location], output_path: str) -> None:
    """
    Export locations to GeoJSON format.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the GeoJSON file

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> export_to_geojson(locations, "output.geojson")
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


def export_to_kml(locations: List[Location], output_path: str) -> None:
    """
    Export locations to KML format with separate folders for each location type.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the KML file

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> export_to_kml(locations, "output.kml")
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


def export_to_all_formats(locations: List[Location], base_path: str) -> None:
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
        # Food & Drink (Red) - matches Google Maps red icons
        "restaurant": "red",
        "cafe": "red",
        "bar": "red",
        # Culture & Arts (Light Blue) - matches Google Maps light blue icons
        "museum": "lightblue",
        "gallery": "lightblue",
        "theater": "lightblue",
        "theatre": "lightblue",
        # Nature & Outdoors (Green) - matches Google Maps green icons
        "park": "green",
        "garden": "green",
        # Shopping & Commerce (Blue) - matches Google Maps blue icons
        "shopping": "blue",
        "store": "blue",
        "market": "blue",
        # Accommodation (Light Gray) - matches Google Maps yellow icons
        # (using light gray as closest)
        "hotel": "lightgray",
        "accommodation": "lightgray",
        # Transport (Gray) - matches Google Maps white icons
        "transport": "gray",
        "station": "gray",
        # Landmarks & Monuments (Orange) - matches Google Maps orange icons
        "landmark": "orange",
        "monument": "orange",
        "church": "orange",
        "temple": "orange",
        # Entertainment & Experiences (Purple) - matches Google Maps purple icons
        "cinema": "purple",
        "entertainment": "purple",
        "theme_park": "purple",
        "experience": "purple",
        # Neighborhoods & Areas (Dark Red) - matches Google Maps red icons
        "neighborhood": "darkred",
        # Passages (Light Blue) - matches Google Maps light blue icons
        "passage": "lightblue",
    }

    return type_colors.get(loc_type.lower(), "gray")


def show_locations_grouped(
    locations: List[Location],
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
        group_name_str = str(group_name)
        if group_by == "type":
            group_display_name = f"📍 {group_name_str.title()} ({len(group_locs)} locations)"
        elif group_by == "neighborhood":
            group_display_name = f"🏘️ {group_name_str} ({len(group_locs)} locations)"
        elif group_by == "date_added":
            group_display_name = f"📅 Added: {group_name_str} ({len(group_locs)} locations)"
        elif group_by == "date_of_visit":
            group_display_name = f"🎯 Visited: {group_name_str} ({len(group_locs)} locations)"
        else:
            group_display_name = (
                f"{str(group_by).title()}: {group_name_str} ({len(group_locs)} locations)"
            )

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
        print(f"   • {str(group_name).title()} ({len(groups[group_name])} locations)")


def show_locations_with_filtering(
    locations: List[Location],
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


def get_available_types(locations: List[Location]) -> List[str]:
    """
    Get a list of all available location types from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique location types

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> types = get_available_types(locations)
        >>> print(f"Available types: {types}")
    """
    return sorted(list(set(loc.get("type", "") for loc in locations if loc.get("type"))))


def get_available_tags(locations: List[Location]) -> List[str]:
    """
    Get a list of all available tags from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique tags across all locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> tags = get_available_tags(locations)
        >>> print(f"Available tags: {tags}")
    """
    all_tags = set()
    for loc in locations:
        if "tags" in loc and isinstance(loc["tags"], list):
            all_tags.update(loc["tags"])
    return sorted(list(all_tags))


def get_available_neighborhoods(locations: List[Location]) -> List[str]:
    """
    Get a list of all available neighborhoods from the locations data.

    Args:
        locations: List of location dictionaries

    Returns:
        List of unique neighborhoods

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> neighborhoods = get_available_neighborhoods(locations)
        >>> print(f"Available neighborhoods: {neighborhoods}")
    """
    return sorted(
        list(set(loc.get("neighborhood", "") for loc in locations if loc.get("neighborhood")))
    )


def filter_locations_by_type(
    locations: List[Location], location_types: List[str]
) -> List[Location]:
    """
    Filter locations by their type.

    Args:
        locations: List of location dictionaries
        location_types: List of types to include

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> restaurants = filter_locations_by_type(locations, ["restaurant", "cafe"])
        >>> print(f"Found {len(restaurants)} food locations")
    """
    return [loc for loc in locations if loc.get("type") in location_types]


def filter_locations_by_tags(locations: List[Location], tags: List[str]) -> List[Location]:
    """
    Filter locations by tags (locations must have at least one of the specified tags).

    Args:
        locations: List of location dictionaries
        tags: List of tags to filter by

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> historic_sites = filter_locations_by_tags(locations, ["historic"])
        >>> print(f"Found {len(historic_sites)} historic locations")
    """
    return [
        loc
        for loc in locations
        if "tags" in loc
        and isinstance(loc["tags"], list)
        and any(tag in loc["tags"] for tag in tags)
    ]


def filter_locations_by_neighborhood(
    locations: List[Location], neighborhoods: List[str]
) -> List[Location]:
    """
    Filter locations by neighborhood.

    Args:
        locations: List of location dictionaries
        neighborhoods: List of neighborhoods to include

    Returns:
        Filtered list of locations

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> downtown = filter_locations_by_neighborhood(locations, ["downtown"])
        >>> print(f"Found {len(downtown)} downtown locations")
    """
    return [loc for loc in locations if loc.get("neighborhood") in neighborhoods]


def get_location_summary(locations: List[Location]) -> Dict[str, Any]:
    """
    Get a summary of location data including counts and available options.

    Args:
        locations: List of location dictionaries

    Returns:
        Dictionary with summary information

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> summary = get_location_summary(locations)
        >>> print(f"Total locations: {summary['total_count']}")
        >>> print(f"Types: {summary['types']}")
    """
    return {
        "total_count": len(locations),
        "types": get_available_types(locations),
        "tags": get_available_tags(locations),
        "neighborhoods": get_available_neighborhoods(locations),
        "type_counts": dict(Counter(loc.get("type", "") for loc in locations)),
        "neighborhood_counts": dict(Counter(loc.get("neighborhood", "") for loc in locations)),
    }


def validate_location_data(locations: List[Location]) -> Dict[str, List[str]]:
    """
    Validate location data and return any issues found.

    Args:
        locations: List of location dictionaries

    Returns:
        Dictionary with validation issues by category

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> issues = validate_location_data(locations)
        >>> if issues['missing_required']:
        >>>     print(f"Missing required fields: {issues['missing_required']}")
    """
    issues: Dict[str, List[str]] = {
        "missing_required": [],
        "invalid_coordinates": [],
        "invalid_dates": [],
    }

    for i, loc in enumerate(locations):
        # Check required fields
        if "name" not in loc or not loc["name"]:
            issues["missing_required"].append(f"Location {i + 1}: missing name")
        if "type" not in loc or not loc["type"]:
            issues["missing_required"].append(f"Location {i + 1}: missing type")
        if "latitude" not in loc or not loc["latitude"]:
            issues["missing_required"].append(f"Location {i + 1}: missing latitude")
        if "longitude" not in loc or not loc["longitude"]:
            issues["missing_required"].append(f"Location {i + 1}: missing longitude")

        # Check coordinate validity
        if "latitude" in loc and "longitude" in loc:
            lat, lon = loc["latitude"], loc["longitude"]
            if not (-90 <= lat <= 90):
                issues["invalid_coordinates"].append(f"Location {i + 1}: invalid latitude {lat}")
            if not (-180 <= lon <= 180):
                issues["invalid_coordinates"].append(f"Location {i + 1}: invalid longitude {lon}")

    return issues


def create_sample_locations() -> List[Location]:
    """
    Create sample location data for testing and examples.

    Returns:
        List of sample location dictionaries

    Example:
        >>> sample_locations = create_sample_locations()
        >>> show_locations_grouped(sample_locations, "sample_map.html")
    """
    return [
        {
            "name": "Eiffel Tower",
            "type": "landmark",
            "latitude": 48.8584,
            "longitude": 2.2945,
            "tags": ["historic", "iconic"],
            "neighborhood": "7th arrondissement",
            "date_added": "2024-01-15",
        },
        {
            "name": "Louvre Museum",
            "type": "museum",
            "latitude": 48.8606,
            "longitude": 2.3376,
            "tags": ["art", "historic"],
            "neighborhood": "1st arrondissement",
            "date_added": "2024-01-15",
        },
        {
            "name": "Notre-Dame Cathedral",
            "type": "church",
            "latitude": 48.8530,
            "longitude": 2.3499,
            "tags": ["historic", "architecture"],
            "neighborhood": "4th arrondissement",
            "date_added": "2024-01-15",
        },
    ]


def show_locations_with_google_maps(
    locations: List[Location],
    group_by: str = "type",
    map_filename: str = "map.html",
    satellite: bool = False,
) -> None:
    """
    Create a folium map with Google Maps tiles showing locations grouped by a specified field.

    Note: This uses Google Maps tiles which are free for personal use but may require
    an API key for commercial use or high volume usage.

    Args:
        locations: List of location dictionaries
        group_by: Field to group markers by (e.g., type, neighborhood, date_added)
        map_filename: Path to save the HTML map
        satellite: Use satellite view instead of street view

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> show_locations_with_google_maps(locations, "map.html")
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
