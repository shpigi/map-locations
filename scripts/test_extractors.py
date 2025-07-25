#!/usr/bin/env python3
"""
Quick test script for extractors module.

This script tests the AI extraction pipeline with both basic text and user input files.
Results are saved to YAML files for analysis.
"""

import os
import sys
import yaml

# Add the project root to the path so we can import map_locations_ai
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from map_locations_ai.agent.pipeline import LocationPipeline


def test_basic_extraction():
    """Test basic text extraction."""
    try:
        pipeline = LocationPipeline()

        # Test with simple text
        text = "Visit the Eiffel Tower in Paris and then go to the Louvre Museum. Meet us at 145 Rue du Temple, 75003 Paris."
        result = pipeline.process_text(text)

        print(f"Extracted {len(result)} locations from simple text:")
        for loc in result:
            print(f"- {loc.name}: {loc.address_or_hint} (confidence: {loc.confidence})")

        # Save to YAML
        output_dir = 'temp/extractors_outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extracted_basic.yaml')

        with open(output_file, 'w') as f:
            yaml.dump([loc.__dict__ for loc in result], f, allow_unicode=True, sort_keys=False)

        print(f"📁 Basic extraction results saved to: {output_file}")
        return result
    except Exception as e:
        print(f"❌ Error in basic extraction test: {e}")
        return []


def test_user_input():
    """Test with real user input file."""
    try:
        pipeline = LocationPipeline()

        # Read user input file
        input_file = 'tests/test_assets/user_input_01.txt'
        if not os.path.exists(input_file):
            print(f"❌ Input file not found: {input_file}")
            return []

        with open(input_file, 'r') as f:
            text = f.read()

        result = pipeline.process_text(text)

        print(f"\nExtracted {len(result)} locations from user input:")
        for i, loc in enumerate(result[:15]):  # Show first 15
            print(f"{i+1:2d}. {loc.name}: {loc.address_or_hint} (confidence: {loc.confidence})")

        if len(result) > 15:
            print(f"... and {len(result) - 15} more locations")

        # Save to YAML
        output_dir = 'temp/extractors_outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extracted_user_input.yaml')

        with open(output_file, 'w') as f:
            yaml.dump([loc.__dict__ for loc in result], f, allow_unicode=True, sort_keys=False)

        print(f"📁 User input results saved to: {output_file}")
        return result
    except Exception as e:
        print(f"❌ Error in user input test: {e}")
        return []


def main():
    """Main test function."""
    print("🧪 Testing Extractors Module")
    print("=" * 50)

    # Test basic extraction
    basic_result = test_basic_extraction()

    print("\n" + "=" * 50)

    # Test user input
    user_result = test_user_input()

    total_extracted = len(basic_result) + len(user_result)
    print(f"\n✅ Total locations extracted: {total_extracted}")

    if total_extracted == 0:
        print("⚠️ No locations were extracted. Check the error messages above.")
        sys.exit(1)
    else:
        print("📁 All results saved to temp/extractors_outputs/")
        print("💡 You can now analyze the YAML files for extraction quality")


if __name__ == "__main__":
    main()
