"""
Data export functions for various formats.

This module handles exporting location data to different formats including
JSON, CSV, GeoJSON, and KML with mobile optimization support.
"""

import csv
import json
import os
from pathlib import Path
from typing import Any, Dict, Set

from .categories import (
    COLOR_CATEGORIES,
    get_kml_color,
    get_location_category,
    get_type_color,
)
from .common import LocationList
from .popup_generators import _generate_google_maps_url, _truncate_description_mobile


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
                "coordinates": [loc.get("longitude", 0.0), loc.get("latitude", 0.0)],
            },
            "properties": {
                "name": loc.get("name", ""),
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


def export_to_kml(
    locations: LocationList,
    output_path: str,
    mobile: bool = False,
    show_full: bool = False,
) -> None:
    """
    Export locations to KML format matching Google My Maps style with proper coloring by type.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the KML file
        mobile: Enable mobile-optimized content with simplified descriptions
        show_full: Show all fields including confidence_score, last_updated, validation_status

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> export_to_kml(locations, "output.kml")
        >>> export_to_kml(locations, "mobile_output.kml", mobile=True)
    """
    # Create directory if needed
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

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
            color = get_type_color(loc_type, format="kml")
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

    # Define field order based on mobile optimization
    # Fields to hide unless show_full is True
    hidden_fields = [
        "confidence_score",
        "last_updated",
        "validation_status",
        "date_added",
        "deduplication",
    ]

    if mobile:
        # Mobile-optimized field order (essential information only)
        all_fields = [
            "type",
            "type_group",
            "address",
            "neighborhood",
            "phone",
            "website",
            "url",
            "official_website",
            "description",
            "tags",
            "google_maps_url",
        ]
    else:
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
            "type_group",
            "website",
            "google_maps_url",
        ]

    # Add any additional fields not in standard list (for non-mobile)
    if not mobile and locations:
        first_loc = locations[0]
        for field in sorted(first_loc.keys()):
            if field not in all_fields and field not in [
                "name",
                "latitude",
                "longitude",
            ]:
                # Skip hidden fields unless show_full is True
                if not show_full and field in hidden_fields:
                    continue
                all_fields.append(field)

    # Add placemarks
    for loc in locations:
        loc_type = loc.get("type", "").lower()
        color = get_type_color(loc_type, format="kml")
        style_id = f"#icon-1899-{color[2:].upper()}-labelson"

        # Get the type group (color category) for this location
        type_group = get_location_category(loc.get("type", ""))

        # Create description based on mobile optimization
        description_parts = ["<![CDATA["]

        if mobile:
            # Mobile-optimized description with simplified content
            description_parts.append(
                f'<div style="font-family: Arial, sans-serif; max-width: 300px;">'
            )
            description_parts.append(
                f'<h3 style="color: #333; margin: 0 0 8px 0;">'
                f'{loc.get("name", "Unnamed Location")}</h3>'
            )

            for field in all_fields:
                value = loc.get(field, "")
                if field == "type_group":
                    # Add type group with color information
                    if type_group and type_group != "Other":
                        category_info = COLOR_CATEGORIES.get(type_group, {})
                        emoji = category_info.get("emoji", "📍")
                        color_hex = category_info.get("hex_color", "#808080")
                        description_parts.append(
                            f'<p style="margin: 4px 0;"><strong>Category:</strong> '
                            f'<span style="color: {color_hex}; font-weight: bold;">'
                            f"{emoji} {type_group}</span></p>"
                        )
                elif field == "google_maps_url":
                    value = _generate_google_maps_url(loc)
                    value_str = str(value) if value else ""
                    if value_str:
                        description_parts.append(
                            f'<p style="margin: 4px 0;"><strong>Directions:</strong> '
                            f'<a href="{value_str}" target="_blank">Open in Maps</a></p>'
                        )
                    else:
                        description_parts.append("google_maps_url: <br>")
                    continue
                elif field == "description":
                    # Limit description to first 100 characters for mobile
                    desc = str(value) if value else ""
                    if desc:
                        formatted_value = _truncate_description_mobile(desc)
                        description_parts.append(
                            f'<p style="margin: 4px 0;"><strong>Description:</strong> '
                            f"{formatted_value}</p>"
                        )
                elif field == "phone" and value:
                    # Make phone numbers clickable for mobile
                    description_parts.append(
                        f'<p style="margin: 4px 0;"><strong>Phone:</strong> '
                        f'<a href="tel:{value}">{value}</a></p>'
                    )
                elif field in ["website", "url", "official_website"] and value:
                    # Make website links open in new tab
                    description_parts.append(
                        f'<p style="margin: 4px 0;"><strong>Website:</strong> '
                        f'<a href="{value}" target="_blank">{value}</a></p>'
                    )
                elif isinstance(value, list):
                    if value:  # Non-empty list
                        value_str = ", ".join(str(item) for item in value)
                    else:
                        value_str = ""
                else:
                    value_str = str(value) if value else ""

                description_parts.append(f"{field}: {value_str}<br>")  # type: ignore

            description_parts.append("</div>")
        else:
            # Standard description format
            for field in all_fields:
                value = loc.get(field, "")
                if field == "type_group":
                    # Add type group with color information
                    if type_group and type_group != "Other":
                        category_info = COLOR_CATEGORIES.get(type_group, {})
                        emoji = category_info.get("emoji", "📍")
                        color_hex = category_info.get("hex_color", "#808080")
                        description_parts.append(
                            f"type_group: {emoji} {type_group} (color: {color_hex})<br>"
                        )
                elif field == "google_maps_url":
                    value = _generate_google_maps_url(loc)
                    value_str = str(value) if value else ""
                    if value_str:
                        description_parts.append(
                            f'google_maps_url: <a href="{value_str}" target="_blank">Link</a><br>'
                        )
                    else:
                        description_parts.append("google_maps_url: <br>")
                    continue
                elif isinstance(value, list):
                    if value:  # Non-empty list
                        value_str = ", ".join(str(item) for item in value)
                    else:
                        value_str = ""
                else:
                    value_str = str(value) if value else ""

                description_parts.append(f"{field}: {value_str}<br>")  # type: ignore

        description_parts.append("]]>")
        description = "".join(description_parts)

        # Create ExtendedData (same for both mobile and desktop)
        extended_data_parts = ["      <ExtendedData>"]
        for field in all_fields:
            value = loc.get(field, "")
            if field == "type_group":
                # Add type group information
                if type_group and type_group != "Other":
                    category_info = COLOR_CATEGORIES.get(type_group, {})
                    emoji = category_info.get("emoji", "📍")
                    color_hex = category_info.get("hex_color", "#808080")
                    value_str = f"{emoji} {type_group} (color: {color_hex})"
                else:
                    value_str = "Other"

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
            elif field == "google_maps_url":
                value = _generate_google_maps_url(loc)
                value_str = str(value) if value else ""
                if value_str:
                    # Always store the actual URL in ExtendedData for Google Maps to use
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
            elif field == "description" and mobile:
                # For mobile, truncate description in ExtendedData too
                desc = str(value) if value else ""
                if desc:
                    value_str = _truncate_description_mobile(desc)
                else:
                    value_str = ""

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
                # Default case for any other field type
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
            f'          {loc.get("longitude", 0.0)},{loc.get("latitude", 0.0)},0',
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
    if mobile:
        print("📱 Mobile-optimized content enabled")

    # Show type distribution
    type_counts: Dict[str, int] = {}
    for loc in locations:
        loc_type = loc.get("type", "unknown")
        type_counts[loc_type] = type_counts.get(loc_type, 0) + 1

    print(f"📋 Created KML with {len(locations)} locations:")
    for loc_type, count in sorted(type_counts.items()):
        color = get_type_color(loc_type, format="kml")
        print(f"   • {loc_type.title()}: {count} locations (color: #{color[2:]})")


def export_to_all_formats(
    locations: LocationList,
    base_path: str,
    mobile: bool = False,
    show_full: bool = False,
) -> None:
    """
    Export locations to all supported formats.

    Args:
        locations (list): List of location dictionaries
        base_path (str): Base path for output files (without extension)
        mobile (bool): Enable mobile-optimized content for KML export
        show_full (bool): Show all fields including confidence_score, last_updated, validation_status
    """
    # Create directory if needed
    output_dir = os.path.dirname(base_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Export to different formats
    export_to_json(locations, f"{base_path}.json")
    export_to_csv(locations, f"{base_path}.csv")
    export_to_geojson(locations, f"{base_path}.geojson")
    export_to_kml(locations, f"{base_path}.kml", mobile=mobile, show_full=show_full)

    # Show output location
    if output_dir:
        print(f"✅ Data formats exported to: {Path(output_dir).resolve()}")
    else:
        print(f"✅ Data formats exported to: {Path.cwd()}")
