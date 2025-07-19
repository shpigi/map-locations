#!/usr/bin/env python3
"""
Basic usage example for map_locations package.

This script demonstrates how to use the map_locations package
to load location data, create maps, and export to various formats.
"""

import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import map_locations
sys.path.insert(0, str(Path(__file__).parent.parent))

from map_locations import (
    load_locations_from_yaml,
    show_locations_grouped,
    export_to_all_formats,
)


def create_sample_data():
    """Create sample location data for demonstration."""
    sample_data = {
        "locations": [
            {
                "name": "Central Park",
                "type": "park",
                "latitude": 40.7829,
                "longitude": -73.9654,
                "tags": ["outdoor", "recreation", "nature"],
                "neighborhood": "Upper East Side",
                "date_added": "2024-01-01",
                "date_of_visit": "2024-01-15",
            },
            {
                "name": "Times Square",
                "type": "landmark",
                "latitude": 40.7580,
                "longitude": -73.9855,
                "tags": ["tourist", "entertainment", "shopping"],
                "neighborhood": "Midtown",
                "date_added": "2024-01-02",
                "date_of_visit": "2024-01-20",
            },
            {
                "name": "Brooklyn Bridge",
                "type": "bridge",
                "latitude": 40.7061,
                "longitude": -73.9969,
                "tags": ["landmark", "architecture", "views"],
                "neighborhood": "Brooklyn",
                "date_added": "2024-01-03",
                "date_of_visit": "2024-01-25",
            },
            {
                "name": "Statue of Liberty",
                "type": "monument",
                "latitude": 40.6892,
                "longitude": -74.0445,
                "tags": ["landmark", "history", "tourist"],
                "neighborhood": "Lower Manhattan",
                "date_added": "2024-01-04",
                "date_of_visit": "2024-01-30",
            },
        ]
    }
    
    # Create examples directory if it doesn't exist
    examples_dir = Path(__file__).parent
    examples_dir.mkdir(exist_ok=True)
    
    # Save sample data to YAML file
    import yaml
    sample_file = examples_dir / "sample_locations.yaml"
    with open(sample_file, "w") as f:
        yaml.dump(sample_data, f, default_flow_style=False)
    
    return str(sample_file)


def main():
    """Main function demonstrating package usage."""
    print("🗺️ Map Locations Package - Basic Usage Example")
    print("=" * 50)
    
    # Create sample data
    print("📝 Creating sample location data...")
    sample_file = create_sample_data()
    print(f"✅ Sample data created: {sample_file}")
    
    # Load locations
    print("\n📂 Loading locations from YAML file...")
    locations = load_locations_from_yaml(sample_file)
    print(f"📍 Loaded {len(locations)} locations")
    
    # Display location information
    print("\n📋 Location Details:")
    for i, location in enumerate(locations, 1):
        print(f"  {i}. {location['name']} ({location['type']})")
        print(f"     📍 {location['latitude']}, {location['longitude']}")
        print(f"     🏘️  {location['neighborhood']}")
        print(f"     🏷️  {', '.join(location['tags'])}")
        print()
    
    # Create output directory
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    # Create interactive map
    print("🗺️ Creating interactive map...")
    map_file = output_dir / "sample_map.html"
    show_locations_grouped(
        locations,
        group_by="type",
        map_filename=str(map_file),
    )
    print(f"✅ Interactive map created: {map_file}")
    
    # Export to all formats
    print("\n📤 Exporting to all formats...")
    export_base = output_dir / "sample_locations"
    export_to_all_formats(locations, str(export_base))
    print(f"✅ All formats exported to: {output_dir}")
    
    # List exported files
    print("\n📁 Exported files:")
    for ext in [".json", ".csv", ".geojson", ".kml"]:
        file_path = export_base.with_suffix(ext)
        if file_path.exists():
            print(f"  📄 {file_path.name}")
    
    print(f"\n🎉 Example completed successfully!")
    print(f"📂 Check the '{output_dir}' directory for generated files.")
    print(f"🌐 Open '{map_file}' in your browser to view the interactive map.")


if __name__ == "__main__":
    main() 