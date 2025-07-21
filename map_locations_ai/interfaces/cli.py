"""
Command-line interface for the location AI agent.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from map_locations.common import load_locations_from_yaml, save_locations_to_yaml

from ..agent.pipeline import LocationPipeline


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="map-locations-ai",
        description="AI agent for automatic location data curation and enrichment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract locations from text
  map-locations-ai extract --text "Visit the Eiffel Tower and Louvre" --region "paris"

  # Process URLs
  map-locations-ai extract --urls "https://travel-blog.com/paris-guide"

  # Enrich existing locations
  map-locations-ai enrich --input locations.yaml --output enriched.yaml

  # Validate location data
  map-locations-ai validate --input locations.yaml
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract locations from text or URLs")
    extract_parser.add_argument("--text", type=str, help="Text containing location mentions")
    extract_parser.add_argument("--urls", nargs="+", help="URLs to process for location extraction")
    extract_parser.add_argument(
        "--region", type=str, help="Region hint for better location resolution"
    )
    extract_parser.add_argument(
        "--output", "-o", type=str, required=True, help="Output YAML file path"
    )

    # Enrich command
    enrich_parser = subparsers.add_parser("enrich", help="Enrich existing location data")
    enrich_parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input YAML file path"
    )
    enrich_parser.add_argument(
        "--output", "-o", type=str, required=True, help="Output YAML file path"
    )
    enrich_parser.add_argument(
        "--sources",
        nargs="+",
        default=["wikipedia", "nominatim"],
        help="Data sources to use for enrichment",
    )

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate location data accuracy")
    validate_parser.add_argument(
        "--input", "-i", type=str, required=True, help="Input YAML file path"
    )
    validate_parser.add_argument(
        "--output", "-o", type=str, help="Output YAML file with validation results"
    )
    validate_parser.add_argument("--report", action="store_true", help="Generate validation report")

    return parser


def handle_extract_command(args) -> int:
    """Handle the extract command."""
    if not args.text and not args.urls:
        print("Error: Must provide either --text or --urls")
        return 1

    try:
        pipeline = LocationPipeline()

        print("🔍 Extracting locations...")
        locations = pipeline.process_mixed_input(text=args.text, urls=args.urls, region=args.region)

        if not locations:
            print("⚠️  No locations found")
            return 0

        print(f"📍 Found {len(locations)} locations")
        save_locations_to_yaml(locations, args.output)
        print("✅ Extraction completed successfully!")

        return 0

    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        return 1


def handle_enrich_command(args) -> int:
    """Handle the enrich command."""
    try:
        # Load existing locations
        print(f"📖 Loading locations from {args.input}...")
        locations = load_locations_from_yaml(args.input)

        if not locations:
            print("⚠️  No locations found in input file")
            return 0

        print(f"📍 Loaded {len(locations)} locations")

        # Enrich locations
        pipeline = LocationPipeline()
        print("🔍 Enriching locations...")
        enriched_locations = pipeline.enrich_existing_locations(locations)

        # Save results
        save_locations_to_yaml(enriched_locations, args.output)
        print("✅ Enrichment completed successfully!")

        return 0

    except Exception as e:
        print(f"❌ Error during enrichment: {e}")
        return 1


def handle_validate_command(args) -> int:
    """Handle the validate command."""
    try:
        # Load locations
        print(f"📖 Loading locations from {args.input}...")
        locations = load_locations_from_yaml(args.input)

        if not locations:
            print("⚠️  No locations found in input file")
            return 0

        print(f"📍 Loaded {len(locations)} locations")

        # Validate locations
        pipeline = LocationPipeline()
        print("🔍 Validating locations...")
        validated_locations = pipeline.validate_locations(locations)

        # Generate report
        if args.report:
            print("\n📊 Validation Report:")
            valid_count = 0
            for i, loc in enumerate(validated_locations):
                confidence = loc.get("confidence_score", 0.0)
                status = loc.get("validation_status", "unknown")
                print(f"  {i+1:2d}. {loc['name']:30s} - {confidence:.2f} ({status})")
                if status == "verified":
                    valid_count += 1

            print(f"\n✅ {valid_count}/{len(locations)} locations validated successfully")

        # Save results if output specified
        if args.output:
            save_locations_to_yaml(validated_locations, args.output)

        return 0

    except Exception as e:
        print(f"❌ Error during validation: {e}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 1

    # Handle commands
    if args.command == "extract":
        return handle_extract_command(args)
    elif args.command == "enrich":
        return handle_enrich_command(args)
    elif args.command == "validate":
        return handle_validate_command(args)
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
