import csv
import json
import os
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, cast

import folium
import yaml

# Import common models
from .common import Location, LocationList, load_locations_from_yaml


def _generate_google_maps_url(location: Union[Dict[str, Any], Location]) -> str:
    """
    Generate a Google Maps URL for a location using name and address.

    Args:
        location: Location dictionary

    Returns:
        Google Maps URL string
    """
    name = location.get("name", "")
    address = location.get("address", "")

    if not name and not address:
        return ""

    # Create query string from name and address
    query_parts = []
    if name:
        query_parts.append(name)
    if address:
        query_parts.append(address)

    query = ", ".join(query_parts)
    encoded_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/maps/search/?api=1&query={encoded_query}"


def _is_url(text: str) -> bool:
    """Check if a string is a URL."""
    url_pattern = re.compile(
        r"^https?://"  # http:// or https://
        r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
        r"localhost|"  # localhost...
        r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
        r"(?::\d+)?"  # optional port
        r"(?:/?|[/?]\S+)$",
        re.IGNORECASE,
    )
    return bool(url_pattern.match(str(text)))


def _format_field_value(field_name: str, value: Any) -> str:
    """Format field value for display, handling special cases like URLs and lists."""
    if value is None or value == "":
        return ""

    # Handle google_maps_url field specially
    if field_name == "google_maps_url" and value:
        return f'<a href="{value}" target="_blank">Link</a>'

    # Handle lists (like tags)
    if isinstance(value, list):
        if not value:  # Empty list
            return ""
        # Check if any items in the list are URLs
        formatted_items = []
        for item in value:
            item_str = str(item)
            if _is_url(item_str):
                formatted_items.append(
                    f'<a href="{item_str}" target="_blank">{item_str}</a>'
                )
            else:
                formatted_items.append(item_str)
        return ", ".join(formatted_items)

    # Handle URLs
    value_str = str(value)
    if _is_url(value_str):
        return f'<a href="{value_str}" target="_blank">{value_str}</a>'

    return value_str


def _generate_popup_html(
    location: Union[Dict[str, Any], Location], style: str = "folium"
) -> str:
    """
    Generate comprehensive HTML popup content for a location.

    Args:
        location: Location dictionary
        style: Style format - 'folium' for folium maps, 'kml' for KML export

    Returns:
        HTML string for popup content
    """
    # Standard field order (these will appear first)
    standard_fields = [
        "name",
        "type",
        "tags",
        "neighborhood",
        "date_added",
        "date_of_visit",
        "description",
        "website",
        "url",
        "phone",
        "address",
        "notes",
        "google_maps_url",
    ]

    # Field display names
    field_names = {
        "name": "Name",
        "type": "Type",
        "tags": "Tags",
        "neighborhood": "Neighborhood",
        "date_added": "Date Added",
        "date_of_visit": "Date of Visit",
        "description": "Description",
        "website": "Website",
        "url": "URL",
        "phone": "Phone",
        "address": "Address",
        "notes": "Notes",
        "google_maps_url": "Google Maps",
        "latitude": "Latitude",
        "longitude": "Longitude",
    }

    # Get all fields in location, starting with standard ones
    all_fields = []
    for field in standard_fields:
        if field == "google_maps_url":
            # Always include google_maps_url since it's calculated
            all_fields.append(field)
        elif field in location:
            all_fields.append(field)

    # Add any additional fields not in standard list (excluding coordinates)
    for field in sorted(location.keys()):
        if field not in standard_fields and field not in ["latitude", "longitude"]:
            all_fields.append(field)

    if style == "kml":
        # KML style with CDATA wrapper
        html_parts = [
            "<![CDATA[",
            '<div style="font-family: Arial, sans-serif; max-width: 350px;">',
            f'<h3 style="color: #333; margin: 0 0 10px 0;">'
            f'{location.get("name", "Unnamed Location")}</h3>',
        ]

        for field in all_fields:
            if field == "name":  # Skip name as it's already in header
                continue

            if field == "google_maps_url":
                value = _generate_google_maps_url(location)
                formatted_value = _format_field_value(field, value)
            else:
                formatted_value = _format_field_value(field, location.get(field))

            if formatted_value:  # Only include non-empty fields
                display_name = field_names.get(field, field.replace("_", " ").title())
                html_parts.append(
                    f'<p style="margin: 5px 0;"><strong>{display_name}:</strong> '
                    f"{formatted_value}</p>"
                )

        html_parts.extend(["</div>", "]]>"])
        return "".join(html_parts)

    else:  # folium style
        html_parts = ["<div>", f'<h4>{location.get("name", "Unnamed Location")}</h4>']

        for field in all_fields:
            if field == "name":  # Skip name as it's already in header
                continue

            if field == "google_maps_url":
                value = _generate_google_maps_url(location)
                formatted_value = _format_field_value(field, value)
            else:
                formatted_value = _format_field_value(field, location.get(field))

            if formatted_value:  # Only include non-empty fields
                display_name = field_names.get(field, field.replace("_", " ").title())
                html_parts.append(
                    f"<p><strong>{display_name}: </strong>{formatted_value}</p>"
                )

        html_parts.append("</div>")
        return "".join(html_parts)


def export_to_json(locations: LocationList, output_path: str) -> None:
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

    # Add Google Maps URL to each location
    locations_with_google_maps = []
    for loc in locations:
        loc_copy = loc.copy()
        loc_copy["google_maps_url"] = _generate_google_maps_url(loc)
        locations_with_google_maps.append(loc_copy)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            {"locations": locations_with_google_maps}, f, indent=2, ensure_ascii=False
        )

    print(f"📄 JSON exported to: {Path(output_path).resolve()}")


def export_to_csv(locations: LocationList, output_path: str) -> None:
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

    # Get all possible fields from all locations and add google_maps_url
    all_fields: Set[str] = set()
    for loc in locations:
        all_fields.update(loc.keys())

    # Add google_maps_url field
    all_fields.add("google_maps_url")

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
            # Add Google Maps URL
            row["google_maps_url"] = _generate_google_maps_url(loc)
            writer.writerow(row)

    print(f"📊 CSV exported to: {Path(output_path).resolve()}")


def export_to_geojson(locations: LocationList, output_path: str) -> None:
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
                "google_maps_url": _generate_google_maps_url(loc),
            },
        }
        geojson["features"].append(feature)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, indent=2, ensure_ascii=False)

    print(f"🗺️ GeoJSON exported to: {Path(output_path).resolve()}")


def export_to_kml(locations: LocationList, output_path: str) -> None:
    """
    Export locations to KML format matching Google My Maps style with proper coloring by type.

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

    # Define type to color mapping (AABBGGRR format - note reversed byte order)
    type_colors = {
        # Food & Drink (Red variants)
        "restaurant": "ff0000ff",  # Red
        "cafe": "ff0000ff",
        "bar": "ff0000ff",
        # Museums (Blue variants)
        "museum": "ffd18802",  # Blue
        "gallery": "ffd18802",
        # Parks (Green)
        "park": "ff42b37c",  # Green
        "garden": "ff42b37c",
        # Landmarks (Orange/Yellow variants)
        "landmark": "ff25a8f9",  # Yellow
        "monument": "ff25a8f9",
        "church": "ff25a8f9",
        "temple": "ff25a8f9",
        # Hotels (Orange/Red)
        "hotel": "ff0051e6",  # Orange-red
        "accommodation": "ff0051e6",
        # Shopping (Purple variants)
        "shopping": "ffb73a67",  # Purple
        "store": "ffb73a67",
        "market": "ffb73a67",
        # Entertainment (Purple)
        "cinema": "ffb0279c",  # Purple
        "entertainment": "ffb0279c",
        "theme_park": "ffb0279c",
        "experience": "ffb0279c",
        # Neighborhoods (Yellow)
        "neighborhood": "ff00eaff",  # Yellow
        # Transport (Gray)
        "transport": "ff646000",  # Gray
        "station": "ff646000",
        # Default
        "bridge": "ff646000",  # Gray
    }

    # Default color for unknown types
    default_color = "ff808080"  # Gray

    # Get unique types and create styles
    all_types = set()
    for loc in locations:
        loc_type = loc.get("type", "").lower()
        all_types.add(loc_type)

    # Start KML content
    kml_content = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<kml xmlns="http://www.opengis.net/kml/2.2">',
        "  <Document>",
        "    <name>Map Locations</name>",
    ]

    # Create styles for each type
    for loc_type in all_types:
        if loc_type:  # Skip empty types
            color = type_colors.get(loc_type, default_color)
            style_id = f"icon-1899-{color[2:].upper()}-labelson"

            style = [
                f'    <Style id="{style_id}">',
                "      <IconStyle>",
                f"        <color>{color}</color>",
                "        <scale>1</scale>",
                "        <Icon>",
                "          <href>https://www.gstatic.com/mapspro/images/stock/"
                "503-wht-blank_maps.png</href>",
                "        </Icon>",
                '        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>',
                "      </IconStyle>",
                "    </Style>",
            ]
            kml_content.extend(style)

    # Add default style
    default_style = [
        '    <Style id="icon-1899-808080-labelson">',
        "      <IconStyle>",
        f"        <color>{default_color}</color>",
        "        <scale>1</scale>",
        "        <Icon>",
        "          <href>https://www.gstatic.com/mapspro/images/stock/"
        "503-wht-blank_maps.png</href>",
        "        </Icon>",
        '        <hotSpot x="32" xunits="pixels" y="64" yunits="insetPixels"/>',
        "      </IconStyle>",
        "    </Style>",
    ]
    kml_content.extend(default_style)

    # Add placemarks
    for loc in locations:
        loc_type = loc.get("type", "").lower()
        color = type_colors.get(loc_type, default_color)
        style_id = f"#icon-1899-{color[2:].upper()}-labelson"

        # Create simple description (field: value<br> format)
        description_parts = ["<![CDATA["]

        # Standard field order for consistent display
        all_fields = [
            "accessibility",
            "address",
            "booking_required",
            "date_added",
            "description",
            "languages",
            "latitude",
            "longitude",
            "neighborhood",
            "opening_hours",
            "phone",
            "price_range",
            "rating",
            "tags",
            "type",
            "website",
            "google_maps_url",
        ]

        # Add any additional fields not in standard list
        for field in sorted(loc.keys()):
            if field not in all_fields and field not in [
                "name",
                "latitude",
                "longitude",
            ]:
                all_fields.append(field)

        for field in all_fields:
            value = loc.get(field, "")
            if field == "google_maps_url":
                value = _generate_google_maps_url(loc)
                value_str = str(value) if value else ""
            elif isinstance(value, list):
                if value:  # Non-empty list
                    value_str = ", ".join(str(item) for item in value)
                else:
                    value_str = ""
            else:
                value_str = str(value) if value else ""

            description_parts.append(f"{field}: {value_str}<br>")

        description_parts.append("]]>")
        description = "".join(description_parts)

        # Create ExtendedData
        extended_data_parts = ["      <ExtendedData>"]
        for field in all_fields:
            value = loc.get(field, "")
            if field == "google_maps_url":
                value = _generate_google_maps_url(loc)
                value_str = str(value) if value else ""
                if value_str:
                    # Handle special characters in value (URLs contain special chars)
                    extended_data_parts.extend(
                        [
                            f'        <Data name="{field}">',
                            f"          <value><![CDATA[{value_str}]]></value>",
                            "        </Data>",
                        ]
                    )
                else:
                    extended_data_parts.extend(
                        [
                            f'        <Data name="{field}">',
                            "          <value/>",
                            "        </Data>",
                        ]
                    )
            elif isinstance(value, list):
                value_str = str(value) if value else ""
                if value_str:
                    extended_data_parts.extend(
                        [
                            f'        <Data name="{field}">',
                            f"          <value><![CDATA[{value_str}]]></value>",
                            "        </Data>",
                        ]
                    )
                else:
                    extended_data_parts.extend(
                        [
                            f'        <Data name="{field}">',
                            "          <value/>",
                            "        </Data>",
                        ]
                    )
            else:
                value_str = str(value) if value else ""
                if value_str:
                    # Handle special characters in value
                    if any(char in value_str for char in ["<", ">", "&", '"']):
                        extended_data_parts.extend(
                            [
                                f'        <Data name="{field}">',
                                f"          <value><![CDATA[{value_str}]]></value>",
                                "        </Data>",
                            ]
                        )
                    else:
                        extended_data_parts.extend(
                            [
                                f'        <Data name="{field}">',
                                f"          <value>{value_str}</value>",
                                "        </Data>",
                            ]
                        )
                else:
                    extended_data_parts.extend(
                        [
                            f'        <Data name="{field}">',
                            "          <value/>",
                            "        </Data>",
                        ]
                    )
        extended_data_parts.append("      </ExtendedData>")
        extended_data = "\n".join(extended_data_parts)

        # Handle location name with CDATA if needed
        location_name = loc.get("name", "Unnamed Location")
        if any(char in location_name for char in ["<", ">", "&", '"']):
            name_element = f"      <name><![CDATA[{location_name}]]></name>"
        else:
            name_element = f"      <name>{location_name}</name>"

        placemark = [
            "    <Placemark>",
            name_element,
            f"      <description>{description}</description>",
            f"      <styleUrl>{style_id}</styleUrl>",
            extended_data,
            "      <Point>",
            "        <coordinates>",
            f'          {loc["longitude"]},{loc["latitude"]},0',
            "        </coordinates>",
            "      </Point>",
            "    </Placemark>",
        ]
        kml_content.extend(placemark)

    # Close KML
    kml_content.extend(["  </Document>", "</kml>"])

    # Write file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(kml_content))

    print(f"🗺️ KML exported to: {Path(output_path).resolve()}")

    # Show type distribution
    type_counts: Dict[str, int] = {}
    for loc in locations:
        loc_type = loc.get("type", "unknown")
        type_counts[loc_type] = type_counts.get(loc_type, 0) + 1

    print(f"📋 Created KML with {len(locations)} locations:")
    for loc_type, count in sorted(type_counts.items()):
        color = type_colors.get(loc_type.lower(), default_color)
        print(f"   • {loc_type.title()}: {count} locations (color: #{color[2:]})")


def export_to_all_formats(locations: LocationList, base_path: str) -> None:
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
    locations: LocationList,
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
            raise ValueError(
                f"No locations found matching the specified types: {filter_types}"
            )

    # Center the map
    first = locations[0]
    m = folium.Map(location=[first["latitude"], first["longitude"]], zoom_start=14)

    # Add additional tile layers based on provider selection
    # The default OpenStreetMap is already added by folium.Map()
    if tile_provider == "google_maps":
        # Add Google Maps as additional base layer option
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attr="Google Maps",
            name="Google Maps",
            overlay=False,
            control=True,
        ).add_to(m)
    elif tile_provider == "google_satellite":
        # Add Google Satellite as additional base layer option
        folium.TileLayer(
            tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
            attr="Google Satellite",
            name="Google Satellite",
            overlay=False,
            control=True,
        ).add_to(m)

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
            group_display_name = (
                f"📍 {group_name_str.title()} ({len(group_locs)} locations)"
            )
        elif group_by == "neighborhood":
            group_display_name = f"🏘️ {group_name_str} ({len(group_locs)} locations)"
        elif group_by == "date_added":
            group_display_name = (
                f"📅 Added: {group_name_str} ({len(group_locs)} locations)"
            )
        elif group_by == "date_of_visit":
            group_display_name = (
                f"🎯 Visited: {group_name_str} ({len(group_locs)} locations)"
            )
        else:
            group_display_name = f"{str(group_by).title()}: {group_name_str} ({len(group_locs)} locations)"

        fg = folium.FeatureGroup(name=group_display_name)
        feature_groups[group_name] = fg

        for loc in group_locs:
            # Get color based on location type
            color = get_type_color(loc.get("type", ""))

            # Create popup content with better styling
            popup_html = _generate_popup_html(loc)

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
    print(
        f"📋 Created {len(feature_groups)} separate groups that can be toggled on/off:"
    )
    for group_name, fg in feature_groups.items():
        print(f"   • {str(group_name).title()} ({len(groups[group_name])} locations)")


def show_locations_with_filtering(
    locations: LocationList,
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


def show_locations_with_advanced_filtering(
    locations: LocationList,
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
    filter_types: Optional[List[str]] = None,
) -> None:
    """
    Create a folium map with advanced filtering capabilities using dropdown controls.
    Users can select a field (type, neighborhood, date_of_visit) and filter by specific values.

    Args:
        locations: List of location dictionaries
        map_filename: Path to save the HTML map
        tile_provider: Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        filter_types: List of location types to pre-filter (optional)

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> show_locations_with_advanced_filtering(locations, "advanced_map.html")
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
            raise ValueError(
                f"No locations found matching the specified types: {filter_types}"
            )

    # Center the map
    first = locations[0]

    # Always start with default OpenStreetMap to avoid URL-named layers
    m = folium.Map(location=[first["latitude"], first["longitude"]], zoom_start=14)

    # Add additional tile layer options for advanced filtering
    # Add Google Maps
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
        attr="Google Maps",
        name="Google Maps",
        overlay=False,
        control=True,
    ).add_to(m)

    # Add Google Satellite
    folium.TileLayer(
        tiles="https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}",
        attr="Google Satellite",
        name="Google Satellite",
        overlay=False,
        control=True,
    ).add_to(m)

    # Collect unique values for each filterable field
    field_values = {
        "type": sorted(
            list(set(loc.get("type", "") for loc in locations if loc.get("type")))
        ),
        "neighborhood": sorted(
            list(
                set(
                    loc.get("neighborhood", "")
                    for loc in locations
                    if loc.get("neighborhood")
                )
            )
        ),
        "date_of_visit": sorted(
            list(
                set(
                    loc.get("date_of_visit", "")
                    for loc in locations
                    if loc.get("date_of_visit")
                )
            )
        ),
        "name": sorted(
            [loc.get("name", f"Location {i + 1}") for i, loc in enumerate(locations)]
        ),
    }

    # Add all markers to the map
    markers_data = []
    for i, loc in enumerate(locations):
        # Get color based on location type
        color = get_type_color(loc.get("type", ""))

        # Create popup content
        popup_html = _generate_popup_html(loc)

        marker = folium.Marker(
            location=[loc["latitude"], loc["longitude"]],
            popup=folium.Popup(popup_html, max_width=450),
            tooltip=loc["name"],
            icon=folium.Icon(color=color),
        )
        marker.add_to(m)

        # Store marker data for JavaScript filtering
        markers_data.append(
            {
                "id": i,
                "type": loc.get("type", ""),
                "neighborhood": loc.get("neighborhood", ""),
                "date_of_visit": loc.get("date_of_visit", ""),
                "name": loc.get("name", f"Location {i + 1}"),
            }
        )

    # Add layer control for tile providers (positioned on top right to avoid filter panel)
    folium.LayerControl(
        position="topright",
        collapsed=False,
        autoZIndex=True,
        overlay=False,
        control=True,
    ).add_to(m)

    # Create the advanced filtering control HTML with multi-selection checkboxes
    filter_control_html = f"""
    <div id="filter-control" style="
        position: fixed;
        top: 80px;
        left: 10px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        z-index: 1000;
        min-width: 320px;
        max-width: 350px;
        max-height: 80vh;
        overflow-y: auto;
        font-family: Arial, sans-serif;
        font-size: 14px;
    ">
        <div style="margin-bottom: 10px;">
            <strong>🔍 Advanced Filter</strong>
        </div>

        <div style="margin-bottom: 10px;">
            <label for="field-select" style="display: block; margin-bottom: 5px; "
                "font-weight: bold;">
                Filter by:
            </label>
            <select id="field-select" style="width: 100%; padding: 5px; border: 1px solid #ccc; "
                "border-radius: 4px;">
                <option value="">-- Select Field --</option>
                <option value="type">Type</option>
                <option value="neighborhood">Neighborhood</option>
                <option value="date_of_visit">Date of Visit</option>
                <option value="name">Location Name</option>
            </select>
        </div>

        <div id="checkbox-container" style="
            display: none;
            margin-bottom: 10px;
            max-height: 300px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 4px;
            background: #fafafa;
        ">
            <div style="margin-bottom: 8px; font-weight: bold;">
                Select values:
            </div>
            <div style="margin-bottom: 8px;">
                <button id="select-all" style="
                    background: #4CAF50;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    margin-right: 5px;
                    font-size: 12px;
                ">Select All</button>
                <button id="select-none" style="
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 12px;
                ">Clear All</button>
            </div>
            <div id="checkbox-list"></div>
        </div>

        <div>
            <button id="apply-filter" style="
                background: #2196F3;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 5px;
            ">Apply Filter</button>
            <button id="clear-filter" style="
                background: #f44336;
                color: white;
                border: none;
                padding: 8px 12px;
                border-radius: 4px;
                cursor: pointer;
                margin-right: 5px;
            ">Clear Filter</button>
        </div>
        <div style="margin-top: 8px;">
            <span id="result-count" style="color: #666; font-size: 12px;">
                Showing all {len(locations)} locations
            </span>
        </div>
    </div>
    """

    # JavaScript for advanced multi-selection filtering
    filter_script = f"""
    <script>
    // Field values data
    const fieldValues = {json.dumps(field_values)};

    // Markers data with location information
    const markersData = {json.dumps(markers_data)};

    // Get references to all markers (they are added in order)
    let allMarkers = [];

    // Wait for map to be ready and collect marker references
    setTimeout(function() {{
        // Find all markers in the map
        window[Object.keys(window).find(key => key.startsWith('map_'))].eachLayer(function(layer) {{
            if (layer instanceof L.Marker) {{
                allMarkers.push(layer);
            }}
        }});

        console.log('Found', allMarkers.length, 'markers');
    }}, 1000);

    // Get DOM elements
    const fieldSelect = document.getElementById('field-select');
    const checkboxContainer = document.getElementById('checkbox-container');
    const checkboxList = document.getElementById('checkbox-list');
    const selectAllBtn = document.getElementById('select-all');
    const selectNoneBtn = document.getElementById('select-none');
    const applyFilterBtn = document.getElementById('apply-filter');
    const clearFilterBtn = document.getElementById('clear-filter');
    const resultCount = document.getElementById('result-count');

    // Handle field selection change
    fieldSelect.addEventListener('change', function() {{
        const selectedField = this.value;

        if (selectedField && fieldValues[selectedField]) {{
            checkboxContainer.style.display = 'block';
            populateCheckboxes(selectedField);
        }} else {{
            checkboxContainer.style.display = 'none';
            showAllMarkers();
        }}
    }});

    // Populate checkboxes for selected field
    function populateCheckboxes(field) {{
        checkboxList.innerHTML = '';
        const values = fieldValues[field];

        values.forEach(function(value, index) {{
            const checkboxId = `checkbox_${{field}}_${{index}}`;
            const displayValue = value || '(empty)';

            const checkboxHtml = `
                <div style="margin-bottom: 5px;">
                    <label style="display: flex; align-items: center; cursor: pointer;">
                        <input type="checkbox" id="${{checkboxId}}" value="${{value}}"
                               style="margin-right: 8px;" checked>
                        <span style="font-size: 13px;">${{displayValue}}</span>
                    </label>
                </div>
            `;
            checkboxList.innerHTML += checkboxHtml;
        }});
    }}

    // Select all checkboxes
    selectAllBtn.addEventListener('click', function() {{
        const checkboxes = checkboxList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = true);
    }});

    // Clear all checkboxes
    selectNoneBtn.addEventListener('click', function() {{
        const checkboxes = checkboxList.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(cb => cb.checked = false);
    }});

    // Apply filter based on selected checkboxes
    applyFilterBtn.addEventListener('click', function() {{
        const selectedField = fieldSelect.value;
        if (!selectedField) {{
            showAllMarkers();
            return;
        }}

        const checkboxes = checkboxList.querySelectorAll('input[type="checkbox"]:checked');
        const selectedValues = Array.from(checkboxes).map(cb => cb.value);

        if (selectedValues.length === 0) {{
            // No values selected - hide all markers
            hideAllMarkers();
            resultCount.textContent = `Showing 0 of {len(locations)} locations`;
            return;
        }}

        let visibleCount = 0;

        allMarkers.forEach(function(marker, index) {{
            if (index < markersData.length) {{
                const markerData = markersData[index];
                const fieldValue = markerData[selectedField] || '';

                if (selectedValues.includes(fieldValue)) {{
                    marker.setOpacity(1);
                    marker._icon.style.display = 'block';
                    if (marker._shadow) marker._shadow.style.display = 'block';
                    visibleCount++;
                }} else {{
                    marker.setOpacity(0);
                    marker._icon.style.display = 'none';
                    if (marker._shadow) marker._shadow.style.display = 'none';
                }}
            }}
        }});

        resultCount.textContent = `Showing ${{visibleCount}} of {len(locations)} locations`;
    }});

    // Clear filter
    clearFilterBtn.addEventListener('click', function() {{
        fieldSelect.value = '';
        checkboxContainer.style.display = 'none';
        showAllMarkers();
    }});

    // Show all markers
    function showAllMarkers() {{
        allMarkers.forEach(function(marker) {{
            marker.setOpacity(1);
            marker._icon.style.display = 'block';
            if (marker._shadow) marker._shadow.style.display = 'block';
        }});

        resultCount.textContent = `Showing all {len(locations)} locations`;
    }}

    // Hide all markers
    function hideAllMarkers() {{
        allMarkers.forEach(function(marker) {{
            marker.setOpacity(0);
            marker._icon.style.display = 'none';
            if (marker._shadow) marker._shadow.style.display = 'none';
        }});
    }}
    </script>
    """

    # Add the control HTML to the map
    m.get_root().html.add_child(folium.Element(filter_control_html))  # type: ignore[attr-defined]
    m.get_root().html.add_child(folium.Element(filter_script))  # type: ignore[attr-defined]

    # Create output directory if needed
    dirname = os.path.dirname(map_filename)
    if dirname:
        os.makedirs(dirname, exist_ok=True)

    m.save(map_filename)
    print(f"🗺️ Advanced filtering map saved to: {Path(map_filename).resolve()}")
    print("🔍 Interactive filtering controls:")
    print(f"   • Filter by type: {len(field_values['type'])} options")
    print(f"   • Filter by neighborhood: {len(field_values['neighborhood'])} options")
    print(f"   • Filter by date of visit: {len(field_values['date_of_visit'])} options")
    print("   • Clear filter button to show all locations")
    if tile_provider != "openstreetmap":
        print("🗺️ Tile layer controls available in top-right corner")


def get_available_types(locations: LocationList) -> List[str]:
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
    return sorted(
        list(set(loc.get("type", "") for loc in locations if loc.get("type")))
    )


def get_available_tags(locations: LocationList) -> List[str]:
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


def get_available_neighborhoods(locations: LocationList) -> List[str]:
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
        list(
            set(
                loc.get("neighborhood", "")
                for loc in locations
                if loc.get("neighborhood")
            )
        )
    )


def filter_locations_by_type(
    locations: LocationList, location_types: List[str]
) -> LocationList:
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


def filter_locations_by_tags(locations: LocationList, tags: List[str]) -> LocationList:
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
    locations: LocationList, neighborhoods: List[str]
) -> LocationList:
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


def get_location_summary(locations: LocationList) -> Dict[str, Any]:
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
        "neighborhood_counts": dict(
            Counter(loc.get("neighborhood", "") for loc in locations)
        ),
    }


def validate_location_data(locations: LocationList) -> Dict[str, List[str]]:
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
                issues["invalid_coordinates"].append(
                    f"Location {i + 1}: invalid latitude {lat}"
                )
            if not (-180 <= lon <= 180):
                issues["invalid_coordinates"].append(
                    f"Location {i + 1}: invalid longitude {lon}"
                )

    return issues


def create_sample_locations() -> LocationList:
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
    locations: LocationList,
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
    yaml_path = (
        "paris_london_trip_locations.yaml"  # Replace with your actual YAML file path
    )
    locations = load_locations_from_yaml(yaml_path)

    # Create interactive map
    show_locations_grouped(
        locations, group_by="type", map_filename="./maps/paris_london_trip/map.html"
    )

    # Export to all formats
    export_to_all_formats(locations, "./maps/paris_london_trip/export")
