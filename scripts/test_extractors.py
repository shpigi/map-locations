#!/usr/bin/env python3
"""
Enhanced test script for extractors module with better recall evaluation.

This script tests the AI extraction pipeline with both basic text and user input files.
Results are saved to YAML files for analysis with detailed recall metrics.
"""

import os
import sys
import yaml
from typing import List, Dict, Any

# Add the project root to the path so we can import map_locations_ai
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from map_locations_ai.agent.pipeline import LocationPipeline
from map_locations_ai.agent.extractors import ExtractedLocation


def analyze_extraction_results(locations: List[ExtractedLocation], test_name: str) -> Dict[str, Any]:
    """
    Analyze extraction results and provide detailed metrics.

    Args:
        locations: List of extracted locations
        test_name: Name of the test for reporting

    Returns:
        Dictionary with analysis metrics
    """
    if not locations:
        return {
            "test_name": test_name,
            "total_locations": 0,
            "confidence_distribution": {},
            "source_type_distribution": {},
            "avg_confidence": 0.0,
            "high_confidence_count": 0,
            "medium_confidence_count": 0,
            "low_confidence_count": 0
        }

    # Confidence distribution
    confidence_dist = {}
    source_type_dist = {}
    high_conf = 0  # >= 0.8
    medium_conf = 0  # 0.5-0.79
    low_conf = 0  # < 0.5

    total_confidence = 0.0

    for loc in locations:
        # Confidence distribution
        conf_key = f"{loc.confidence:.1f}"
        confidence_dist[conf_key] = confidence_dist.get(conf_key, 0) + 1

        # Source type distribution
        source_type_dist[loc.source_type] = source_type_dist.get(loc.source_type, 0) + 1

        # Confidence categories
        if loc.confidence >= 0.8:
            high_conf += 1
        elif loc.confidence >= 0.5:
            medium_conf += 1
        else:
            low_conf += 1

        total_confidence += loc.confidence

    avg_confidence = total_confidence / len(locations)

    return {
        "test_name": test_name,
        "total_locations": len(locations),
        "confidence_distribution": confidence_dist,
        "source_type_distribution": source_type_dist,
        "avg_confidence": round(avg_confidence, 3),
        "high_confidence_count": high_conf,
        "medium_confidence_count": medium_conf,
        "low_confidence_count": low_conf,
        "high_confidence_percentage": round((high_conf / len(locations)) * 100, 1) if locations else 0
    }


def test_basic_extraction():
    """Test basic text extraction with enhanced analysis."""
    try:
        pipeline = LocationPipeline()

        # Test with simple text
        text = "Visit the Eiffel Tower in Paris and then go to the Louvre Museum. Meet us at 145 Rue du Temple, 75003 Paris."
        result = pipeline.process_text(text)

        print(f"Extracted {len(result)} locations from simple text:")
        for loc in result:
            print(f"- {loc.name}: {loc.address_or_hint} (confidence: {loc.confidence})")

        # Analyze results
        analysis = analyze_extraction_results(result, "Basic Extraction")
        print(f"\n📊 Analysis:")
        print(f"  Total locations: {analysis['total_locations']}")
        print(f"  Average confidence: {analysis['avg_confidence']}")
        print(f"  High confidence: {analysis['high_confidence_count']} ({analysis['high_confidence_percentage']}%)")
        print(f"  Source types: {analysis['source_type_distribution']}")

        # Save to YAML
        output_dir = 'temp/extractors_outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extracted_basic.yaml')
        analysis_file = os.path.join(output_dir, 'analysis_basic.yaml')

        with open(output_file, 'w') as f:
            yaml.dump([loc.__dict__ for loc in result], f, allow_unicode=True, sort_keys=False)

        with open(analysis_file, 'w') as f:
            yaml.dump(analysis, f, allow_unicode=True, sort_keys=False)

        print(f"📁 Basic extraction results saved to: {output_file}")
        print(f"📊 Analysis saved to: {analysis_file}")
        return result, analysis
    except Exception as e:
        print(f"❌ Error in basic extraction test: {e}")
        import traceback
        traceback.print_exc()
        return [], {}


def test_user_input():
    """Test with real user input file with enhanced analysis."""
    try:
        pipeline = LocationPipeline()

        # Read user input file
        input_file = 'tests/test_assets/user_input_01.txt'
        if not os.path.exists(input_file):
            print(f"❌ Input file not found: {input_file}")
            return [], {}

        with open(input_file, 'r') as f:
            text = f.read()

        result = pipeline.process_text(text)

        print(f"\nExtracted {len(result)} locations from user input:")
        for i, loc in enumerate(result[:15]):  # Show first 15
            print(f"{i+1:2d}. {loc.name}: {loc.address_or_hint} (confidence: {loc.confidence})")

        if len(result) > 15:
            print(f"... and {len(result) - 15} more locations")

        # Analyze results
        analysis = analyze_extraction_results(result, "User Input Extraction")
        print(f"\n📊 Analysis:")
        print(f"  Total locations: {analysis['total_locations']}")
        print(f"  Average confidence: {analysis['avg_confidence']}")
        print(f"  High confidence: {analysis['high_confidence_count']} ({analysis['high_confidence_percentage']}%)")
        print(f"  Medium confidence: {analysis['medium_confidence_count']}")
        print(f"  Low confidence: {analysis['low_confidence_count']}")
        print(f"  Source types: {analysis['source_type_distribution']}")
        print(f"  Confidence distribution: {analysis['confidence_distribution']}")

        # Save to YAML
        output_dir = 'temp/extractors_outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extracted_user_input.yaml')
        analysis_file = os.path.join(output_dir, 'analysis_user_input.yaml')

        with open(output_file, 'w') as f:
            yaml.dump([loc.__dict__ for loc in result], f, allow_unicode=True, sort_keys=False)

        with open(analysis_file, 'w') as f:
            yaml.dump(analysis, f, allow_unicode=True, sort_keys=False)

        print(f"📁 User input results saved to: {output_file}")
        print(f"📊 Analysis saved to: {analysis_file}")
        return result, analysis
    except Exception as e:
        print(f"❌ Error in user input test: {e}")
        import traceback
        traceback.print_exc()
        return [], {}


def test_enhanced_extraction():
    """Test enhanced extraction with specific focus areas."""
    try:
        pipeline = LocationPipeline()

        # Test with text that should trigger enhanced patterns
        test_text = """
        Day 1: Museums and Culture
        - 10am: Louvre Museum (book tickets online)
        - 2pm: Musée d'Orsay (impressionist art)
        - 6pm: Meet at Place de la Concorde
        - 8pm: Dinner at Le Marais district

        Accommodation: Hotel de Ville, 123 Main Street, 75001 Paris
        Meeting point: Metro Blanche station, look for yellow umbrella

        Places to visit:
        - Eiffel Tower (must see)
        - Arc de Triomphe
        - Sacré-Cœur Basilica
        - Notre Dame Cathedral (currently closed)
        - Luxembourg Gardens
        - Champs-Élysées shopping
        """

        result = pipeline.process_text(test_text)

        print(f"\nEnhanced extraction test - extracted {len(result)} locations:")
        for i, loc in enumerate(result):
            print(f"{i+1:2d}. {loc.name} ({loc.source_type}, conf: {loc.confidence})")

        # Analyze results
        analysis = analyze_extraction_results(result, "Enhanced Extraction")
        print(f"\n📊 Enhanced Analysis:")
        print(f"  Total locations: {analysis['total_locations']}")
        print(f"  Average confidence: {analysis['avg_confidence']}")
        print(f"  High confidence: {analysis['high_confidence_count']} ({analysis['high_confidence_percentage']}%)")

        # Save results
        output_dir = 'temp/extractors_outputs'
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, 'extracted_enhanced.yaml')
        analysis_file = os.path.join(output_dir, 'analysis_enhanced.yaml')

        with open(output_file, 'w') as f:
            yaml.dump([loc.__dict__ for loc in result], f, allow_unicode=True, sort_keys=False)

        with open(analysis_file, 'w') as f:
            yaml.dump(analysis, f, allow_unicode=True, sort_keys=False)

        print(f"📁 Enhanced extraction results saved to: {output_file}")
        return result, analysis
    except Exception as e:
        print(f"❌ Error in enhanced extraction test: {e}")
        import traceback
        traceback.print_exc()
        return [], {}


def compare_with_previous_results():
    """Compare current results with previous extraction to measure improvement."""
    try:
        # Load previous results if they exist
        previous_file = 'temp/extractors_outputs/extracted_user_input.yaml'
        if os.path.exists(previous_file):
            with open(previous_file, 'r') as f:
                previous_results = yaml.safe_load(f)

            print(f"\n📈 Comparison with previous results:")
            print(f"  Previous total: {len(previous_results)}")

            # Count high confidence results
            high_conf_prev = sum(1 for loc in previous_results if loc.get('confidence', 0) >= 0.8)
            print(f"  Previous high confidence: {high_conf_prev}")

            return len(previous_results), high_conf_prev
        else:
            print("No previous results found for comparison")
            return 0, 0
    except Exception as e:
        print(f"Error comparing results: {e}")
        return 0, 0


def main():
    """Main test function with enhanced evaluation."""
    print("🧪 Enhanced Extractors Module Testing")
    print("=" * 60)

    # Test basic extraction
    basic_result, basic_analysis = test_basic_extraction()

    print("\n" + "=" * 60)

    # Test user input
    user_result, user_analysis = test_user_input()

    print("\n" + "=" * 60)

    # Test enhanced extraction
    enhanced_result, enhanced_analysis = test_enhanced_extraction()

    print("\n" + "=" * 60)

    # Summary statistics
    total_extracted = len(basic_result) + len(user_result) + len(enhanced_result)
    total_high_conf = (
        basic_analysis.get('high_confidence_count', 0) +
        user_analysis.get('high_confidence_count', 0) +
        enhanced_analysis.get('high_confidence_count', 0)
    )

    print("📊 SUMMARY STATISTICS:")
    print(f"  Total locations extracted: {total_extracted}")
    print(f"  Total high confidence: {total_high_conf}")

    if total_extracted > 0:
        overall_high_conf_percentage = (total_high_conf / total_extracted) * 100
        print(f"  Overall high confidence rate: {overall_high_conf_percentage:.1f}%")

    # Compare with previous results
    prev_total, prev_high_conf = compare_with_previous_results()
    if prev_total > 0:
        improvement = total_extracted - prev_total
        print(f"  Improvement in total locations: {improvement:+d}")
        if prev_high_conf > 0:
            high_conf_improvement = total_high_conf - prev_high_conf
            print(f"  Improvement in high confidence: {high_conf_improvement:+d}")

    if total_extracted == 0:
        print("⚠️ No locations were extracted. Check the error messages above.")
        sys.exit(1)
    else:
        print("📁 All results saved to temp/extractors_outputs/")
        print("💡 You can now analyze the YAML files for extraction quality")
        print("🎯 Focus on improving recall while maintaining precision")


if __name__ == "__main__":
    main()
