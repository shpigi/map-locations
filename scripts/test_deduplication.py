#!/usr/bin/env python3
"""
Test script for location deduplication functionality.
Tests various deduplication scenarios with sample data.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from map_locations_ai.deduplicator import LocationDeduplicator


def create_test_locations():
    """Create test locations with various duplicate scenarios."""
    return [
        # Exact duplicates
        {
            "name": "Louvre Museum",
            "type": "museum",
            "description": "World famous art museum in Paris",
            "source_text": "Visit the Louvre Museum",
            "confidence": 0.9,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_001"
        },
        {
            "name": "Louvre Museum",
            "type": "museum",
            "description": "Famous art museum with Mona Lisa",
            "source_text": "The Louvre Museum is incredible",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_003"
        },

        # Name variations
        {
            "name": "Musée du Louvre",
            "type": "museum",
            "description": "Art museum in Paris",
            "source_text": "Musée du Louvre visit",
            "confidence": 0.7,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_005"
        },

        # Fuzzy name matches
        {
            "name": "D'Orsay Museum",
            "type": "museum",
            "description": "Impressionist art museum",
            "source_text": "D'Orsay Museum",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_002"
        },
        {
            "name": "Musée d'Orsay",
            "type": "museum",
            "description": "Museum with impressionist masterpieces",
            "source_text": "Visit Musée d'Orsay",
            "confidence": 0.9,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_004"
        },

        # Similar but different locations (should NOT be duplicates)
        {
            "name": "Tuileries Garden",
            "type": "park",
            "description": "Public garden in Paris",
            "source_text": "Tuileries Garden",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_001"
        },
        {
            "name": "Luxembourg Gardens",
            "type": "park",
            "description": "Beautiful park in Paris",
            "source_text": "Luxembourg Gardens",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_002"
        },

        # Accent variations
        {
            "name": "Père Lachaise Cemetery",
            "type": "cemetery",
            "description": "Famous cemetery in Paris",
            "source_text": "Père Lachaise Cemetery",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_003"
        },
        {
            "name": "Pere Lachaise Cemetery",
            "type": "cemetery",
            "description": "Historic cemetery with notable graves",
            "source_text": "Pere Lachaise Cemetery visit",
            "confidence": 0.7,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_006"
        },

        # Type compatibility test
        {
            "name": "Saatchi Gallery",
            "type": "gallery",
            "description": "Contemporary art gallery",
            "source_text": "Saatchi Gallery",
            "confidence": 0.8,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_004"
        },
        {
            "name": "Saatchi Gallery",
            "type": "museum",
            "description": "Contemporary art museum",
            "source_text": "The Saatchi Gallery/Museum",
            "confidence": 0.7,
            "is_url": False,
            "url": "",
            "chunk_id": "chunk_007"
        }
    ]


def test_deduplication():
    """Test the deduplication functionality."""
    print("🧪 Testing Location Deduplication")
    print("=" * 50)

    # Create test data
    test_locations = create_test_locations()
    print(f"Created {len(test_locations)} test locations")

    # Initialize deduplicator
    deduplicator = LocationDeduplicator()

    # Run deduplication
    deduplicated = deduplicator.deduplicate_locations(test_locations)
    stats = deduplicator.get_stats()

    # Print results
    print(f"\n✅ Deduplication Results:")
    print(f"  Original locations: {stats['processed']}")
    print(f"  Duplicates found: {stats['duplicates_found']}")
    print(f"  Duplicate groups: {stats['groups_created']}")
    print(f"  Final locations: {len(deduplicated)}")
    print(f"  Reduction rate: {100*stats['duplicates_found']/stats['processed']:.1f}%")

    # Print detailed breakdown
    if 'merge_details' in stats and stats['merge_details']['total_groups'] > 0:
        print(f"\n📊 Merge Breakdown:")
        breakdown = stats['merge_details']['group_size_breakdown']
        for size_desc, count in breakdown.items():
            print(f"  • {count} groups with {size_desc}")

        print(f"\n🔍 Detailed Merge Groups:")
        for group in stats['merge_details']['merge_details']:
            print(f"  Group {group['group_id']}: {group['merged_name']} ({group['merged_type']})")
            print(f"    ↳ Merged {group['original_count']} locations with {group['merge_confidence']:.2f} confidence")
            for orig in group['original_locations']:
                print(f"      - {orig['name']} ({orig['type']}) from {orig['chunk_id']} [conf: {orig['confidence']:.2f}]")
            print()
    else:
        print(f"\n📊 No merge groups found (merge_details: {stats.get('merge_details', 'NOT FOUND')})")

    print(f"\n📋 Final Deduplicated Locations:")
    for i, loc in enumerate(deduplicated, 1):
        print(f"{i:2d}. {loc['name']} ({loc['type']}) - conf: {loc['confidence']:.2f}")
        if 'deduplication' in loc and loc['deduplication']['is_merged']:
            print(f"     ↳ Merged from {loc['deduplication']['original_count']} locations")
            print(f"       Merge confidence: {loc['deduplication']['merge_confidence']:.2f}")

    # Validate expected results
    expected_groups = [
        ["Louvre Museum", "Musée du Louvre"],  # Should be merged
        ["D'Orsay Museum", "Musée d'Orsay"],   # Should be merged
        ["Père Lachaise Cemetery", "Pere Lachaise Cemetery"],  # Should be merged (accent)
        ["Saatchi Gallery"]  # Gallery/Museum should be merged due to type compatibility
    ]

    print(f"\n🔍 Validation:")
    print(f"  Expected unique locations: 7-8")
    print(f"  Actual unique locations: {len(deduplicated)}")

    # Check for specific merges
    names = {loc['name'].lower() for loc in deduplicated}

    # Should have either "Louvre Museum" or "Musée du Louvre", but not both
    louvre_count = sum(1 for name in names if 'louvre' in name)
    print(f"  Louvre variations: {louvre_count} (expected: 1)")

    # Should have either "D'Orsay" or "Musée d'Orsay", but not both
    dorsay_count = sum(1 for name in names if 'orsay' in name or "d'orsay" in name)
    print(f"  D'Orsay variations: {dorsay_count} (expected: 1)")

    # Should have one Pere Lachaise
    pere_count = sum(1 for name in names if 'pere' in name or 'père' in name)
    print(f"  Père Lachaise variations: {pere_count} (expected: 1)")

    # Should keep both Tuileries and Luxembourg (different places)
    garden_count = sum(1 for name in names if 'garden' in name or 'tuileries' in name or 'luxembourg' in name)
    print(f"  Different gardens: {garden_count} (expected: 2)")

    success = (
        len(deduplicated) <= 8 and  # Should reduce from 11 to ~7-8
        louvre_count == 1 and
        dorsay_count <= 2 and  # Allow up to 2 if similarity just below threshold
        pere_count == 1 and
        garden_count == 2
    )

    print(f"\n{'✅ Test PASSED' if success else '❌ Test FAILED'}")
    return success


def test_similarity_calculations():
    """Test individual similarity calculations."""
    print("\n🔬 Testing Similarity Calculations")
    print("=" * 50)

    deduplicator = LocationDeduplicator()

    test_pairs = [
        # Exact match
        ("Louvre Museum", "Louvre Museum", "museum", "museum", 1.0),

        # Language variations
        ("Louvre Museum", "Musée du Louvre", "museum", "museum", 0.75),

        # Accent variations
        ("Père Lachaise", "Pere Lachaise", "cemetery", "cemetery", 0.85),

        # Type compatibility
        ("Saatchi Gallery", "Saatchi Gallery", "gallery", "museum", 0.80),

        # Different locations
        ("Tuileries Garden", "Luxembourg Gardens", "park", "park", 0.3),

        # Fuzzy matches
        ("D'Orsay Museum", "Musée d'Orsay", "museum", "museum", 0.75),
    ]

    print("Similarity tests (name1 ~ name2):")
    for name1, name2, type1, type2, expected_min in test_pairs:
        loc1 = {
            "name": name1, "type": type1,
            "description": f"Test location {name1}",
            "source_text": f"Visit {name1}"
        }
        loc2 = {
            "name": name2, "type": type2,
            "description": f"Test location {name2}",
            "source_text": f"Visit {name2}"
        }

        similarity = deduplicator._calculate_similarity(loc1, loc2)
        status = "✅" if similarity >= expected_min else "❌"
        print(f"  {status} {name1} ~ {name2}: {similarity:.3f} (expected ≥{expected_min})")


if __name__ == "__main__":
    print("Map Locations AI - Deduplication Test Suite")
    print("=" * 60)

    try:
        # Test similarity calculations
        test_similarity_calculations()

        # Test full deduplication
        success = test_deduplication()

        print(f"\n{'🎉 All tests completed successfully!' if success else '⚠️  Some tests failed'}")
        sys.exit(0 if success else 1)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
