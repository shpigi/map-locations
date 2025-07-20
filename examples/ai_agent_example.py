#!/usr/bin/env python3
"""
AI Agent Example for Map Locations

This example demonstrates how AI agents can effectively use the map_locations package
for data analysis, validation, filtering, and visualization.
"""

from pathlib import Path
from typing import List

from map_locations import (
    Location,
    create_sample_locations,
    export_to_all_formats,
    filter_locations_by_neighborhood,
    filter_locations_by_tags,
    filter_locations_by_type,
    get_available_neighborhoods,
    get_available_tags,
    get_available_types,
    get_location_summary,
    load_locations_from_yaml,
    show_locations_grouped,
    show_locations_with_filtering,
    validate_location_data,
)


def demonstrate_data_loading() -> List[Location]:
    """
    Demonstrate different ways to load location data.

    Returns:
        List of location dictionaries
    """
    print("🔍 Demonstrating data loading...")

    # Method 1: Load from existing YAML file
    yaml_path = "sample_locations.yaml"
    if Path(yaml_path).exists():
        locations = load_locations_from_yaml(yaml_path)
        print(f"✅ Loaded {len(locations)} locations from {yaml_path}")
    else:
        # Method 2: Create sample data
        locations = create_sample_locations()
        print(f"✅ Created {len(locations)} sample locations")

    return locations


def demonstrate_data_validation(locations: List[Location]) -> bool:
    """
    Demonstrate data validation capabilities.

    Args:
        locations: List of location dictionaries

    Returns:
        True if data is valid, False otherwise
    """
    print("\n🔍 Demonstrating data validation...")

    issues = validate_location_data(locations)

    if any(issues.values()):
        print("❌ Data validation issues found:")
        for category, problems in issues.items():
            if problems:
                print(f"  {category}: {problems}")
        return False
    else:
        print("✅ Data validation passed - all locations are valid")
        return True


def demonstrate_data_analysis(locations: List[Location]) -> None:
    """
    Demonstrate data analysis capabilities.

    Args:
        locations: List of location dictionaries
    """
    print("\n📊 Demonstrating data analysis...")

    # Get comprehensive summary
    summary = get_location_summary(locations)

    print(f"📈 Dataset Summary:")
    print(f"  Total locations: {summary['total_count']}")
    print(f"  Available types: {summary['types']}")
    print(f"  Available tags: {summary['tags']}")
    print(f"  Available neighborhoods: {summary['neighborhoods']}")

    # Show type distribution
    print(f"\n📊 Type Distribution:")
    for loc_type, count in summary["type_counts"].items():
        if loc_type:  # Skip empty types
            print(f"  {loc_type}: {count} locations")

    # Show neighborhood distribution
    print(f"\n🏘️ Neighborhood Distribution:")
    for neighborhood, count in summary["neighborhood_counts"].items():
        if neighborhood:  # Skip empty neighborhoods
            print(f"  {neighborhood}: {count} locations")


def demonstrate_filtering(locations: List[Location]) -> None:
    """
    Demonstrate filtering capabilities.

    Args:
        locations: List of location dictionaries
    """
    print("\n🔍 Demonstrating filtering capabilities...")

    # Get available options for filtering
    available_types = get_available_types(locations)
    available_tags = get_available_tags(locations)
    available_neighborhoods = get_available_neighborhoods(locations)

    print(f"Available filtering options:")
    print(f"  Types: {available_types}")
    print(f"  Tags: {available_tags}")
    print(f"  Neighborhoods: {available_neighborhoods}")

    # Filter by type
    if "museum" in available_types:
        museums = filter_locations_by_type(locations, ["museum"])
        print(f"\n🏛️ Found {len(museums)} museums")
        for museum in museums:
            print(f"  - {museum['name']} ({museum.get('neighborhood', 'Unknown area')})")

    # Filter by tags
    if "historic" in available_tags:
        historic_sites = filter_locations_by_tags(locations, ["historic"])
        print(f"\n🏛️ Found {len(historic_sites)} historic sites")
        for site in historic_sites:
            print(f"  - {site['name']} ({site['type']})")

    # Filter by neighborhood
    if available_neighborhoods:
        first_neighborhood = available_neighborhoods[0]
        neighborhood_locations = filter_locations_by_neighborhood(locations, [first_neighborhood])
        print(f"\n🏘️ Found {len(neighborhood_locations)} locations in {first_neighborhood}")
        for loc in neighborhood_locations:
            print(f"  - {loc['name']} ({loc['type']})")


def demonstrate_visualization(locations: List[Location]) -> None:
    """
    Demonstrate visualization capabilities.

    Args:
        locations: List of location dictionaries
    """
    print("\n🗺️ Demonstrating visualization capabilities...")

    # Create output directory
    output_dir = Path("ai_agent_examples")
    output_dir.mkdir(exist_ok=True)

    # Create different types of maps
    print("Creating interactive maps...")

    # 1. Basic grouped map
    show_locations_grouped(
        locations, group_by="type", map_filename=str(output_dir / "basic_map.html")
    )
    print(f"✅ Created basic map: {output_dir / 'basic_map.html'}")

    # 2. Map with filtering interface
    show_locations_with_filtering(locations, map_filename=str(output_dir / "filtered_map.html"))
    print(f"✅ Created filtered map: {output_dir / 'filtered_map.html'}")

    # 3. Filtered maps for specific categories
    if "museum" in get_available_types(locations):
        museums = filter_locations_by_type(locations, ["museum"])
        show_locations_grouped(museums, map_filename=str(output_dir / "museums_map.html"))
        print(f"✅ Created museums map: {output_dir / 'museums_map.html'}")

    if "historic" in get_available_tags(locations):
        historic_sites = filter_locations_by_tags(locations, ["historic"])
        show_locations_grouped(
            historic_sites, map_filename=str(output_dir / "historic_sites_map.html")
        )
        print(f"✅ Created historic sites map: {output_dir / 'historic_sites_map.html'}")


def demonstrate_export(locations: List[Location]) -> None:
    """
    Demonstrate export capabilities.

    Args:
        locations: List of location dictionaries
    """
    print("\n📤 Demonstrating export capabilities...")

    # Create output directory
    output_dir = Path("ai_agent_examples/exports")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Export to all formats
    export_to_all_formats(locations, str(output_dir / "complete_dataset"))
    print(f"✅ Exported to all formats in: {output_dir / 'complete_dataset'}")

    # List exported files
    export_files = list(output_dir.glob("complete_dataset.*"))
    print(f"📁 Exported files:")
    for file_path in export_files:
        print(f"  - {file_path.name}")


def demonstrate_complete_workflow() -> None:
    """
    Demonstrate a complete AI agent workflow.
    """
    print("🤖 AI Agent Complete Workflow Demo")
    print("=" * 50)

    # Step 1: Load data
    locations = demonstrate_data_loading()

    # Step 2: Validate data
    is_valid = demonstrate_data_validation(locations)
    if not is_valid:
        print("❌ Cannot proceed with invalid data")
        return

    # Step 3: Analyze data
    demonstrate_data_analysis(locations)

    # Step 4: Filter data
    demonstrate_filtering(locations)

    # Step 5: Visualize data
    demonstrate_visualization(locations)

    # Step 6: Export data
    demonstrate_export(locations)

    print("\n🎉 Complete workflow demonstration finished!")
    print("📁 Check the 'ai_agent_examples' directory for generated files")


def demonstrate_ai_agent_patterns() -> None:
    """
    Demonstrate common AI agent usage patterns.
    """
    print("\n🤖 AI Agent Usage Patterns")
    print("=" * 40)

    # Pattern 1: Quick data exploration
    print("\n📊 Pattern 1: Quick Data Exploration")
    locations = create_sample_locations()
    summary = get_location_summary(locations)
    print(f"Dataset contains {summary['total_count']} locations")
    print(f"Types available: {summary['types']}")

    # Pattern 2: Data validation before processing
    print("\n✅ Pattern 2: Data Validation")
    issues = validate_location_data(locations)
    if not any(issues.values()):
        print("Data is valid, proceeding with analysis")
    else:
        print("Data has issues, need to fix before proceeding")

    # Pattern 3: Filtered analysis
    print("\n🔍 Pattern 3: Filtered Analysis")
    cultural_sites = filter_locations_by_type(locations, ["museum", "gallery"])
    historic_sites = filter_locations_by_tags(locations, ["historic"])
    print(f"Cultural sites: {len(cultural_sites)}")
    print(f"Historic sites: {len(historic_sites)}")

    # Pattern 4: Batch processing
    print("\n⚙️ Pattern 4: Batch Processing")
    location_types = get_available_types(locations)
    for loc_type in location_types:
        filtered_locations = filter_locations_by_type(locations, [loc_type])
        print(f"Processing {loc_type}: {len(filtered_locations)} locations")

    # Pattern 5: Error handling
    print("\n🛡️ Pattern 5: Error Handling")
    try:
        # Simulate loading from non-existent file
        locations = load_locations_from_yaml("non_existent_file.yaml")
    except FileNotFoundError:
        print("File not found, using sample data instead")
        locations = create_sample_locations()

    print("✅ All patterns demonstrated successfully!")


if __name__ == "__main__":
    # Run the complete workflow demonstration
    demonstrate_complete_workflow()

    # Run AI agent patterns demonstration
    demonstrate_ai_agent_patterns()
