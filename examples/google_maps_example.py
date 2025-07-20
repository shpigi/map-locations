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

from map_locations.core import create_sample_locations, show_locations_grouped


def main() -> None:
    """Demonstrate Google Maps tile providers."""

    # Use sample data instead of loading from file
    locations = create_sample_locations()

    print(f"📍 Loaded {len(locations)} sample locations")

    # Create output directory
    import os

    os.makedirs("./maps/google_maps_example", exist_ok=True)

    # Create map with OpenStreetMap (default)
    print("🗺️ Creating map with OpenStreetMap tiles...")
    show_locations_grouped(
        locations,
        group_by="type",
        map_filename="./maps/google_maps_example/map_osm.html",
        tile_provider="openstreetmap",
    )

    # Create map with Google Maps
    print("🗺️ Creating map with Google Maps tiles...")
    show_locations_grouped(
        locations,
        group_by="type",
        map_filename="./maps/google_maps_example/map_google.html",
        tile_provider="google_maps",
    )

    # Create map with Google Satellite
    print("🗺️ Creating map with Google Satellite tiles...")
    show_locations_grouped(
        locations,
        group_by="type",
        map_filename="./maps/google_maps_example/map_satellite.html",
        tile_provider="google_satellite",
    )

    print("✅ All maps created successfully!")
    print("📁 Check the maps/google_maps_example/ directory for the generated HTML files")


if __name__ == "__main__":
    main()
