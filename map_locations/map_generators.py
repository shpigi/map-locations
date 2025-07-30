"""
Interactive map generation and visualization functions.

This module handles the creation of interactive maps using Folium, including
various grouping options, filtering capabilities, and mobile optimization.
"""

import json
import os
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

import folium

from .categories import (
    COLOR_CATEGORIES,
    FOLIUM_TO_HEX_COLORS,
    filter_locations_by_category,
    get_location_category,
    get_type_color,
)
from .common import LocationList
from .popup_generators import _generate_mobile_popup_html, _generate_popup_html


def show_locations_grouped(
    locations: LocationList,
    group_by: str = "type",
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
    filter_types: Optional[List[str]] = None,
    filter_categories: Optional[List[str]] = None,
    mobile: bool = False,
) -> None:
    """
    Create a folium map showing locations grouped by a specified field.

    Args:
        locations (list): List of dicts loaded from YAML.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added, category).
        map_filename (str): Path to save the HTML map.
        tile_provider (str): Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        filter_types (list, optional): List of location types to include.
        filter_categories (list, optional): List of color categories to include.
        mobile (bool): Enable mobile-optimized popups and layout.
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

    # Filter locations by category if filter_categories is provided
    if filter_categories:
        locations = filter_locations_by_category(locations, filter_categories)
        if not locations:
            raise ValueError(
                f"No locations found matching the specified categories: {filter_categories}"
            )

    # Center the map
    first = locations[0]
    m = folium.Map(
        location=[first.get("latitude", 0.0), first.get("longitude", 0.0)],
        zoom_start=14,
    )

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
        if group_by == "category":
            key = get_location_category(loc.get("type", ""))
        else:
            key = loc.get(group_by, "Unknown")
        groups[key].append(loc)

    # Create feature groups with better naming
    feature_groups = {}
    for group_name, group_locs in groups.items():
        # Create a more descriptive group name
        group_name_str = str(group_name)

        if group_by == "category":
            # Use category info for display
            category_info = COLOR_CATEGORIES.get(group_name_str, {})
            emoji = category_info.get("emoji", "📍")
            group_display_name = (
                f"{emoji} {group_name_str} ({len(group_locs)} locations)"
            )
        elif group_by == "type":
            # Get category for type-based grouping
            category = get_location_category(group_name_str)
            category_info = COLOR_CATEGORIES.get(category, {})
            emoji = category_info.get("emoji", "📍")
            group_display_name = (
                f"{emoji} {group_name_str.title()} ({len(group_locs)} locations)"
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
            marker_color: str = str(get_type_color(loc.get("type", "")))  # type: ignore

            # Create popup content with mobile optimization
            if mobile:
                popup_html = _generate_mobile_popup_html(loc)
                popup_width = 300  # Narrower for mobile
            else:
                popup_html = _generate_popup_html(loc)
                popup_width = 450  # Standard width for desktop

            folium.Marker(
                location=[loc.get("latitude", 0.0), loc.get("longitude", 0.0)],
                popup=folium.Popup(popup_html, max_width=popup_width),
                tooltip=loc.get("name", ""),
                icon=folium.Icon(color=marker_color),
            ).add_to(fg)

        fg.add_to(m)

    # Add layer control with mobile optimization
    if mobile:
        # For mobile, add a collapsible layer control button
        layer_control_html = """
        <div id="layer-control" style="
            position: fixed;
            top: 10px;
            right: 10px;
            background: white;
            padding: 10px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            z-index: 1000;
            min-width: 200px;
            max-width: 250px;
            max-height: 70vh;
            overflow-y: auto;
            font-family: Arial, sans-serif;
            font-size: 13px;
            display: none;
        ">
            <div style="margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center;">
                <strong>🗺️ Layers</strong>
                <button id="close-layer-control" style="
                    background: #f44336;
                    color: white;
                    border: none;
                    padding: 2px 6px;
                    border-radius: 3px;
                    cursor: pointer;
                    font-size: 11px;
                ">✕</button>
            </div>
            <div id="layer-control-content">
                <!-- Layer control content will be moved here by JavaScript -->
            </div>
        </div>

        <button id="toggle-layer-control" style="
            position: fixed;
            top: 10px;
            right: 10px;
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            z-index: 1001;
            font-size: 12px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.2);
        ">🗺️ Layers</button>
        """

        layer_control_script = """
        <script>
        // Get DOM elements
        const toggleLayerControlBtn = document.getElementById('toggle-layer-control');
        const closeLayerControlBtn = document.getElementById('close-layer-control');
        const layerControl = document.getElementById('layer-control');
        const layerControlContent = document.getElementById('layer-control-content');

        // Move the default layer control to our custom container
        setTimeout(function() {
            // Find the default layer control
            const defaultLayerControl = document.querySelector('.leaflet-control-layers');
            if (defaultLayerControl) {
                // Hide the default layer control
                defaultLayerControl.style.display = 'none';

                // Move its content to our custom container
                layerControlContent.innerHTML = defaultLayerControl.innerHTML;

                // Style the moved content for mobile
                const checkboxes = layerControlContent.querySelectorAll('input[type="checkbox"]');
                checkboxes.forEach(function(checkbox) {
                    checkbox.style.marginRight = '8px';
                });

                const labels = layerControlContent.querySelectorAll('label');
                labels.forEach(function(label) {
                    label.style.fontSize = '12px';
                    label.style.marginBottom = '6px';
                    label.style.display = 'flex';
                    label.style.alignItems = 'center';
                });
            }
        }, 1000);

        // Toggle layer control panel visibility
        toggleLayerControlBtn.addEventListener('click', function() {
            if (layerControl.style.display === 'none') {
                layerControl.style.display = 'block';
                toggleLayerControlBtn.textContent = '🗺️ Hide Layers';
            } else {
                layerControl.style.display = 'none';
                toggleLayerControlBtn.textContent = '🗺️ Layers';
            }
        });

        // Close layer control panel
        closeLayerControlBtn.addEventListener('click', function() {
            layerControl.style.display = 'none';
            toggleLayerControlBtn.textContent = '🗺️ Layers';
        });
        </script>
        """

        # Add the custom layer control HTML and script to the map
        m.get_root().html.add_child(folium.Element(layer_control_html))  # type: ignore
        m.get_root().html.add_child(folium.Element(layer_control_script))  # type: ignore

        # Add the default layer control (will be moved by JavaScript)
        folium.LayerControl(
            position="topright",
            collapsed=False,
            autoZIndex=True,
            overlay=True,
            control=True,
        ).add_to(m)
    else:
        # Desktop version - use standard layer control
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
    if mobile:
        print("📱 Mobile-optimized layout enabled")
        print("🗺️ Collapsible layer controls:")
        print("   • Toggle button in top-right corner")
        print("   • Layer panel can be shown/hidden")
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
    filter_categories: Optional[List[str]] = None,
    group_by: str = "type",
    mobile: bool = False,
) -> None:
    """
    Create a folium map with filtering capabilities for location types or categories.

    Args:
        locations (list): List of dicts loaded from YAML.
        map_filename (str): Path to save the HTML map.
        tile_provider (str): Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        filter_types (list, optional): List of location types to include.
        filter_categories (list, optional): List of color categories to include.
        group_by (str): Field to group markers by (e.g., type, neighborhood, date_added, category).
        mobile (bool): Enable mobile-optimized popups and layout.
    """
    show_locations_grouped(
        locations=locations,
        group_by=group_by,
        map_filename=map_filename,
        tile_provider=tile_provider,
        filter_types=filter_types,
        filter_categories=filter_categories,
        mobile=mobile,
    )


def show_locations_with_google_maps(
    locations: LocationList,
    group_by: str = "type",
    map_filename: str = "map.html",
    satellite: bool = False,
    mobile: bool = False,
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
        mobile: Enable mobile-optimized popups and layout

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> show_locations_with_google_maps(locations, "map.html")
    """
    tile_provider = "google_satellite" if satellite else "google_maps"
    show_locations_grouped(
        locations, group_by, map_filename, tile_provider, mobile=mobile
    )


def show_locations_by_category(
    locations: LocationList,
    categories: Optional[List[str]] = None,
    map_filename: str = "map.html",
    tile_provider: str = "openstreetmap",
    mobile: bool = False,
) -> None:
    """
    Create a folium map showing locations grouped by color categories.

    Args:
        locations: List of location dictionaries
        categories: List of categories to include (e.g., ["Food & Drink", "Culture & Arts"])
        map_filename: Path to save the HTML map
        tile_provider: Map tile provider ('openstreetmap', 'google_maps', 'google_satellite')
        mobile: Enable mobile-optimized popups and layout

    Example:
        >>> locations = load_locations_from_yaml("locations.yaml")
        >>> show_locations_by_category(locations, ["Food & Drink", "Culture & Arts"])
    """
    show_locations_grouped(
        locations=locations,
        group_by="category",
        map_filename=map_filename,
        tile_provider=tile_provider,
        filter_categories=categories,
        mobile=mobile,
    )
