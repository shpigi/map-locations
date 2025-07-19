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
  # Create an interactive map (grouped by type by default)
  map-locations map passages.yaml --output maps/passages/map.html

  # Export to all formats
  map-locations export passages.yaml --output maps/passages/passages

  # Export to specific format
  map-locations export passages.yaml --format json --output maps/passages/passages.json

  # Create map grouped by neighborhood
  map-locations map passages.yaml --group-by neighborhood --output maps/passages/map.html
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Map command
    map_parser = subparsers.add_parser("map", help="Create an interactive map from YAML file")
    map_parser.add_argument(
        "yaml_file",
        type=str,
        help="Path to YAML file containing location data",
    )
    map_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default="map.html",
        help="Output path for the HTML map (default: map.html)",
    )
    map_parser.add_argument(
        "--group-by",
        "-g",
        type=str,
        default="type",
        choices=["neighborhood", "type", "date_added", "date_of_visit"],
        help="Field to group markers by (default: type)",
    )

    # Export command
    export_parser = subparsers.add_parser("export", help="Export locations to various formats")
    export_parser.add_argument(
        "yaml_file",
        type=str,
        help="Path to YAML file containing location data",
    )
    export_parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help=(
            "Output path (without extension for all formats, or with extension for specific format)"
        ),
    )
    export_parser.add_argument(
        "--format",
        "-f",
        type=str,
        choices=["json", "csv", "geojson", "kml", "all"],
        default="all",
        help="Export format (default: all)",
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


def handle_map_command(args: argparse.Namespace) -> None:
    """Handle the map command."""
    try:
        # Load locations
        print(f"📂 Loading locations from: {args.yaml_file}")
        locations = load_locations_from_yaml(args.yaml_file)

        if not locations:
            print("❌ No locations found in the YAML file.")
            sys.exit(1)

        print(f"📍 Loaded {len(locations)} locations")

        # Create map
        print("🗺️ Creating interactive map...")
        show_locations_grouped(
            locations,
            group_by=args.group_by,
            map_filename=args.output,
        )

        print("✅ Map created successfully!")

    except Exception as e:
        print(f"❌ Error creating map: {e}")
        sys.exit(1)


def handle_export_command(args: argparse.Namespace) -> None:
    """Handle the export command."""
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

        if args.format == "all":
            # Export to all formats
            print("📤 Exporting to all formats...")
            export_to_all_formats(locations, str(output_path))
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
                export_to_kml(locations, str(output_path))

        print("✅ Export completed successfully!")

    except Exception as e:
        print(f"❌ Error during export: {e}")
        sys.exit(1)


def main(args: Optional[List[str]] = None) -> None:
    """Main entry point for the CLI."""
    parser = create_parser()
    parsed_args = parser.parse_args(args)

    if not parsed_args.command:
        parser.print_help()
        sys.exit(1)

    # Validate YAML file
    validate_yaml_file(parsed_args.yaml_file)

    # Handle commands
    if parsed_args.command == "map":
        handle_map_command(parsed_args)
    elif parsed_args.command == "export":
        handle_export_command(parsed_args)
    else:
        print(f"❌ Unknown command: {parsed_args.command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
