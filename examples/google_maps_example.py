#!/usr/bin/env python3
"""
Example demonstrating Google Maps integration with map_locations.

This example shows how to create maps using Google Maps tiles instead of OpenStreetMap.
Google Maps tiles are free for personal use but may require an API key for commercial use.

CLI Examples:
    # Create map with Google Maps tiles
    map-locations passages.yaml --tile-provider google_maps --output map_google.html

    # Create map with Google Satellite view
    map-locations passages.yaml --tile-provider google_satellite --output map_satellite.html

    # Create map with OpenStreetMap (default)
    map-locations passages.yaml --tile-provider openstreetmap --output map_osm.html
"""

from map_locations.core import load_locations_from_yaml, show_locations_grouped


def main() -> None:
    """Demonstrate Google Maps tile providers."""

    # Load sample data
    yaml_path = "../passages.yaml"  # Look in parent directory
    locations = load_locations_from_yaml(yaml_path)

    print(f"📍 Loaded {len(locations)} locations")

    # Create map with OpenStreetMap (default)
    print("🗺️ Creating map with OpenStreetMap tiles...")
    show_locations_grouped(
        locations,
        group_by="neighborhood",
        map_filename="./maps/passages/map_osm.html",
        tile_provider="openstreetmap",
    )

    # Create map with Google Maps
    print("🗺️ Creating map with Google Maps tiles...")
    show_locations_grouped(
        locations,
        group_by="neighborhood",
        map_filename="./maps/passages/map_google.html",
        tile_provider="google_maps",
    )

    # Create map with Google Satellite
    print("🗺️ Creating map with Google Satellite tiles...")
    show_locations_grouped(
        locations,
        group_by="neighborhood",
        map_filename="./maps/passages/map_satellite.html",
        tile_provider="google_satellite",
    )

    print("✅ All maps created successfully!")
    print("📁 Check the maps/ directory for the generated HTML files")


if __name__ == "__main__":
    main()
