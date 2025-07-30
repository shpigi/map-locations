#!/usr/bin/env python3
"""
Command-line interface for map_locations package.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .core import (
    export_to_all_formats,
    export_to_csv,
    export_to_geojson,
    export_to_json,
    export_to_kml,
    load_locations_from_yaml,
    show_locations_grouped,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="Map Locations - Interactive mapping and export tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create an interactive HTML map (grouped by type by default)
  map-locations passages.yaml --output maps/passages/map.html

  # Create map with Google Maps tiles (locations grouped by type)
  map-locations passages.yaml --tile-provider google_maps --output maps/passages/map.html

  # Create map with Google Satellite view (locations grouped by type)
  map-locations passages.yaml --tile-provider google_satellite --output maps/passages/map.html

  # Create mobile-optimized map with collapsible layer controls
  map-locations passages.yaml --mobile --output maps/passages/mobile_map.html

  # Export to JSON format
  map-locations passages.yaml --format json --output maps/passages/locations.json

  # Export to CSV format
  map-locations passages.yaml --format csv --output maps/passages/locations.csv

  # Export to GeoJSON format
  map-locations passages.yaml --format geojson --output maps/passages/locations.geojson

  # Export to KML format (with grouped folders for Google Maps)
  map-locations passages.yaml --format kml --output maps/passages/locations.kml

  # Export to all formats (JSON, CSV, GeoJSON, KML, HTML)
  map-locations passages.yaml --format all --output maps/passages/locations

  # Create map grouped by neighborhood (instead of type)
  map-locations passages.yaml --group-by neighborhood --output maps/passages/map.html

Note: When creating HTML maps, locations are automatically grouped by type (or other field)
and can be toggled on/off using the layer controls in the top-right corner of the map.

Mobile mode (--mobile) optimizes the layout for mobile devices with:
- Collapsible layer controls (toggle button in top-right corner)
- Simplified popup content (essential information only)
- Narrower popup width (300px vs 450px)
- Clickable phone numbers and website links
- Mobile-optimized KML content (simplified descriptions, clickable links)

KML exports create separate folders for each location type, allowing you to toggle
groups on/off when imported into Google Maps. Mobile KML exports include simplified
descriptions optimized for mobile viewing applications.
        """,
    )

    parser.add_argument(
        "yaml_file",
        type=str,
        help="Path to YAML file containing location data",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="map.html",
        help="Output path (default: map.html for HTML, or specify extension for other formats)",
    )
    parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["html", "json", "csv", "geojson", "kml", "all"],
        default="html",
        help="Export format (default: html)",
    )
    parser.add_argument(
        "--group-by",
        "-g",
        type=str,
        default="type",
        choices=["neighborhood", "type", "date_added", "date_of_visit"],
        help="Field to group markers by (default: type). Groups can be toggled on/off in the map.",
    )
    parser.add_argument(
        "--tile-provider",
        type=str,
        default="openstreetmap",
        choices=["openstreetmap", "google_maps", "google_satellite"],
        help="Map tile provider for HTML maps (default: openstreetmap)",
    )
    parser.add_argument(
        "--mobile",
        action="store_true",
        help="Enable mobile-optimized layout with collapsible filtering controls and "
        "simplified popup content",
    )

    return parser


def validate_yaml_file(yaml_path: str) -> None:
    """Validate that the YAML file exists and is readable."""
    path = Path(yaml_path)
    if not path.exists():
        print(f"❌ Error: YAML file '{yaml_path}' does not exist.")
        sys.exit(1)
    if not path.is_file():
        print(f"❌ Error: '{yaml_path}' is not a file.")
        sys.exit(1)


def handle_command(args: argparse.Namespace) -> None:
    """Handle the main command."""
    try:
        # Load locations
        print(f"📂 Loading locations from: {args.yaml_file}")
        locations = load_locations_from_yaml(args.yaml_file)

        if not locations:
            print("❌ No locations found in the YAML file.")
            sys.exit(1)

        print(f"📍 Loaded {len(locations)} locations")

        # Determine output path
        output_path = Path(args.output)

        if args.format == "html":
            # Create HTML map
            print("🗺️ Creating interactive map...")
            show_locations_grouped(
                locations,
                group_by=args.group_by,
                map_filename=args.output,
                tile_provider=args.tile_provider,
                mobile=args.mobile,
            )
            print("✅ Map created successfully!")

        elif args.format == "all":
            # Export to all formats including HTML
            print("📤 Exporting to all formats...")
            export_to_all_formats(locations, str(output_path), mobile=args.mobile)

            # Also create HTML map
            html_path = output_path.with_suffix(".html")
            print("🗺️ Creating interactive HTML map...")
            show_locations_grouped(
                locations,
                group_by=args.group_by,
                map_filename=str(html_path),
                tile_provider=args.tile_provider,
                mobile=args.mobile,
            )
            print("✅ All formats exported successfully!")

        else:
            # Export to specific format
            if not output_path.suffix:
                output_path = output_path.with_suffix(f".{args.format}")

            print(f"📤 Exporting to {args.format.upper()} format...")

            if args.format == "json":
                export_to_json(locations, str(output_path))
            elif args.format == "csv":
                export_to_csv(locations, str(output_path))
            elif args.format == "geojson":
                export_to_geojson(locations, str(output_path))
            elif args.format == "kml":
                export_to_kml(locations, str(output_path), mobile=args.mobile)
            else:
                print(f"❌ Unknown format: {args.format}")
                sys.exit(1)

            print("✅ Export completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    # Validate YAML file
    validate_yaml_file(parsed_args.yaml_file)

    # Handle the command
    handle_command(parsed_args)


if __name__ == "__main__":
    main()
