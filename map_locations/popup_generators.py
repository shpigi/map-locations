"""
HTML popup generation for location data.

This module handles the generation of HTML popups for locations in different
formats including desktop, mobile-optimized, and KML-compatible versions.
"""

import re
import urllib.parse
from typing import Any, Dict, Union

from .common import Location


def _truncate_description_mobile(description: str, max_chars: int = 200) -> str:
    """
    Truncate description for mobile display to first two sentences or max_chars, whichever is shorter.

    Args:
        description (str): The description text to truncate
        max_chars (int): Maximum number of characters allowed

    Returns:
        str: Truncated description
    """
    if not description:
        return ""

    desc = str(description).strip()

    # Find the end of the second sentence
    sentences = []
    current_sentence = ""

    for char in desc:
        current_sentence += char
        if char in ".!?":
            sentences.append(current_sentence.strip())
            current_sentence = ""
            if len(sentences) >= 2:
                break

    # If we have a partial sentence, add it
    if current_sentence.strip():
        sentences.append(current_sentence.strip())

    # Get the first two sentences
    two_sentences = " ".join(sentences[:2])

    # Truncate to max_chars if needed
    if len(two_sentences) > max_chars:
        truncated = two_sentences[:max_chars]
        # Try to end at a word boundary
        last_space = truncated.rfind(" ")
        if (
            last_space > max_chars * 0.8
        ):  # Only use word boundary if it's not too far back
            truncated = truncated[:last_space]
        return truncated + "..."

    return two_sentences


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


def _generate_mobile_popup_html(location: Union[Dict[str, Any], Location]) -> str:
    """
    Generate mobile-friendly HTML popup content for a location.

    Args:
        location: Location dictionary

    Returns:
        HTML string for mobile popup content
    """
    # Mobile-optimized field order (only essential information)
    mobile_fields = [
        "name",
        "type",
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

    # Field display names
    field_names = {
        "name": "Name",
        "type": "Type",
        "address": "Address",
        "neighborhood": "Neighborhood",
        "phone": "Phone",
        "website": "Website",
        "url": "URL",
        "official_website": "Official Website",
        "description": "Description",
        "tags": "Tags",
        "google_maps_url": "Directions",
    }

    html_parts = ["<div>", f'<h4>{location.get("name", "Unnamed Location")}</h4>']

    for field in mobile_fields:
        if field == "name":  # Skip name as it's already in header
            continue

        if field == "google_maps_url":
            value = _generate_google_maps_url(location)
            formatted_value = _format_field_value(field, value)
        elif field == "description":
            # Limit description to first 100 characters
            desc: str = str(location.get(field, ""))
            if desc:
                formatted_value = _truncate_description_mobile(desc)
            else:
                formatted_value = ""
        elif field == "phone":
            # Make phone numbers clickable for mobile
            phone: str = str(location.get(field, ""))
            if phone:
                formatted_value = f'<a href="tel:{phone}">{phone}</a>'
            else:
                formatted_value = ""
        elif field == "website" or field == "url" or field == "official_website":
            # Make website links open in new tab
            url: str = str(location.get(field, ""))
            if url:
                formatted_value = f'<a href="{url}" target="_blank">{url}</a>'
            else:
                formatted_value = ""
        else:
            formatted_value = _format_field_value(field, location.get(field))

        if formatted_value:  # Only include non-empty fields
            display_name = field_names.get(field, field.replace("_", " ").title())
            html_parts.append(
                f"<p><strong>{display_name}: </strong>{formatted_value}</p>"
            )

    html_parts.append("</div>")
    return "".join(html_parts)
