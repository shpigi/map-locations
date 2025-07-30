# AI Agent Guide

Complete guide for AI agents using the Map Locations package.

## Table of Contents

- [Overview](#overview)
- [Core Data Structure](#core-data-structure)
- [Quick Start for AI Agents](#quick-start-for-ai-agents)
- [AI Processing Pipeline](#ai-processing-pipeline)
- [Enhanced AI Features](#enhanced-ai-features)
- [Data Validation](#data-validation)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

This package provides a comprehensive AI-agent friendly approach with direct OpenAI LLM integration, modular processing components, comprehensive tracing, and YAML-based data processing. The AI functionality is included as a module within the main `map-locations` package.

**Recent AI Enhancements:**
- **LLM-Assisted Geocoding**: AI-powered coordinate extraction as fallback
- **Global Location Support**: Worldwide compatibility without city assumptions
- **Multi-threaded URL Processing**: Improved performance for web scraping
- **Mobile Optimization**: Mobile-optimized map generation and layout
- **Enhanced Error Recovery**: Better handling of API failures and malformed responses

## Core Data Structure

```python
from map_locations import Location

# Location is a TypedDict with the following structure:
Location = {
    "name": str,           # Required: Location name
    "type": str,           # Required: Location type/category
    "latitude": float,      # Required: Latitude coordinate
    "longitude": float,     # Required: Longitude coordinate
    "tags": List[str],      # Optional: List of tags for filtering
    "neighborhood": str,    # Optional: Neighborhood or area name
    "date_added": str,      # Optional: Date when added (YYYY-MM-DD)
    "date_of_visit": str,   # Optional: Date of visit (YYYY-MM-DD)
    "description": str,     # Optional: AI-generated description
    "source_text": str,     # Optional: Exact text from AI extraction
    "confidence": float,    # Optional: AI confidence score (0.1-0.9)
    "is_url": bool,        # Optional: Whether source is a URL
    "url": str,            # Optional: Source URL if applicable
    "address": str,        # Optional: Full address if available
    "extraction_method": str, # Optional: How location was extracted
    "google_maps_url": str, # Optional: Generated Google Maps URL
}
```

## Quick Start for AI Agents

```python
from map_locations import (
    load_locations_from_yaml,
    create_sample_locations,
    get_location_summary,
    filter_locations_by_type,
    validate_location_data,
    show_locations_grouped,
    export_to_all_formats,
)

# Load existing data or create sample data
locations = load_locations_from_yaml("my_locations.yaml")
# OR
locations = create_sample_locations()

# Get summary of available data
summary = get_location_summary(locations)
print(f"Total locations: {summary['total_count']}")
print(f"Available types: {summary['types']}")
print(f"Available tags: {summary['tags']}")

# Validate data for issues
issues = validate_location_data(locations)
if issues['missing_required']:
    print(f"Data issues found: {issues}")

# Filter and visualize
restaurants = filter_locations_by_type(locations, ["restaurant", "cafe"])
show_locations_grouped(restaurants, "restaurants_map.html")

# Create mobile-optimized map
show_locations_grouped(restaurants, "mobile_restaurants_map.html", mobile=True)

# Export to multiple formats
export_to_all_formats(locations, "exports/my_locations")
```

## AI Processing Pipeline

### Modular Architecture

The AI processing is built with a modular architecture for easy extension and maintenance:

```python
from map_locations_ai.pipeline import LocationExtractionPipeline
from map_locations_ai.processors import (
    TextProcessor,
    LLMProcessor,
    YAMLProcessor,
    TraceManager,
    FileManager,
    ConfigManager,
)

# Initialize pipeline
pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")

# Process text file
result = pipeline.process_file("input.txt")

print(f"Extracted {result['total_locations']} locations")
print(f"Processed {result['total_chunks']} chunks")
print(f"Trace file: {result['trace_file']}")
```

### Pipeline Components

#### TextProcessor
- **File Reading**: Reads and chunks text files
- **Chunking**: 100-line chunks with 10-line overlap
- **Line Tracking**: Preserves line numbers for debugging

#### LLMProcessor
- **OpenAI Integration**: Direct API calls to GPT-4o-mini
- **Prompt Management**: Optimized prompts for location extraction
- **Error Handling**: Comprehensive error recovery
- **Rate Limiting**: Configurable API call delays
- **LLM Geocoding**: AI-assisted coordinate extraction as fallback

#### YAMLProcessor
- **YAML Generation**: Creates structured location data
- **Auto-Fixing**: Handles malformed LLM responses
- **Validation**: Required field checking
- **Partial Recovery**: Extracts data from broken responses

#### TraceManager
- **Comprehensive Logging**: All operations logged immediately
- **JSON Format**: Structured trace files
- **Timing Information**: Performance metrics
- **Error Capture**: Complete error context

#### FileManager
- **Backup System**: Automatic backup creation and restoration
- **File I/O**: Safe file operations
- **Cleanup**: Resource management
- **Error Recovery**: Graceful failure handling

#### ConfigManager
- **Configuration Loading**: YAML configuration parsing
- **Validation**: Config parameter validation
- **Defaults**: Sensible default values
- **Environment**: Environment variable support

### Pipeline Features

The `LocationExtractionPipeline` provides:

- **File Processing**: Process text files in chunks
- **LLM Integration**: Direct OpenAI API calls for location extraction
- **YAML Output**: Generate structured location data
- **Error Recovery**: Auto-fix malformed YAML responses
- **Comprehensive Tracing**: Log all LLM calls for debugging
- **Chunk Management**: Process large files in manageable chunks
- **URL Processing**: Extract location info from web pages with multi-threading
- **Deduplication**: Smart duplicate detection and merging
- **LLM Geocoding**: AI-assisted coordinate extraction for missing coordinates

### Configuration
```yaml
# map_locations_ai/config.yaml
llm:
  model: "gpt-4o-mini"
  temperature: 0.1
  max_tokens: 4000  # Increased for larger responses
  timeout: 120

processing:
  chunk_size: 50
  overlap_size: 10

output:
  temp_dir: "map_locations_ai/temp"
  trace_dir: "map_locations_ai/trace"

deduplication:
  similarity_threshold: 0.70
  name_weight: 0.4
  type_weight: 0.2
  description_weight: 0.25
  source_weight: 0.15

geocoding:
  enable_llm_fallback: true
  confidence_threshold: 0.7
  max_retries: 3
```

### Output Structure
```
map_locations_ai/
├── temp/chunk_001.yaml          # Individual chunk results
├── temp/chunk_002.yaml
├── temp/merged.yaml             # Combined results
├── trace/trace_TIMESTAMP.json   # Individual LLM call traces
└── trace/run_TIMESTAMP.json     # Complete run summary
```

### Processing Result
```python
result = pipeline.process_file("input.txt")

# Result contains:
{
    "input_file": "input.txt",
    "total_chunks": 5,
    "total_locations": 134,
    "chunk_files": ["temp/chunk_001.yaml", "temp/chunk_002.yaml", ...],
    "trace_file": "trace/run_20250115_143022.json",
    "geocoding_stats": {
        "llm_geocoding_attempts": 12,
        "llm_geocoding_successes": 8,
        "average_confidence": 0.75
    }
}
```

## Enhanced AI Features

### LLM-Assisted Geocoding

The AI pipeline now includes LLM-assisted geocoding as a fallback when coordinates are missing:

```python
from map_locations_ai.processors.geocoding_service import GeocodingService

# Initialize geocoding service
geocoding = GeocodingService("map_locations_ai/config.yaml")

# Process locations with missing coordinates
locations_with_coords = geocoding.process_locations(locations)

# Check geocoding results
for location in locations_with_coords:
    if location.get("latitude") and location.get("longitude"):
        confidence = location.get("geocoding_confidence", 0.0)
        print(f"✅ {location['name']}: {location['latitude']}, {location['longitude']} (confidence: {confidence})")
    else:
        print(f"❌ {location['name']}: No coordinates found")
```

### Multi-threaded URL Processing

Enhanced URL processing with improved performance:

```python
from map_locations_ai.processors.url_verifier import URLVerifier

# Initialize URL verifier with multi-threading
url_verifier = URLVerifier("map_locations_ai/config.yaml")

# Process URLs with improved performance
verified_urls = url_verifier.verify_urls_batch(url_list)

# Check verification results
for url, status in verified_urls.items():
    if status["valid"]:
        print(f"✅ {url}: {status['response_time']}ms")
    else:
        print(f"❌ {url}: {status['error']}")
```

### Mobile Optimization

Create mobile-optimized maps for better mobile device experience:

```python
from map_locations import show_locations_grouped, show_locations_with_google_maps

# Create mobile-optimized map
show_locations_grouped(
    locations,
    map_filename="mobile_map.html",
    mobile=True
)

# Create mobile map with Google Maps tiles
show_locations_with_google_maps(
    locations,
    map_filename="mobile_google_map.html",
    mobile=True
)
```

### Enhanced Error Recovery

Improved error handling and recovery mechanisms:

```python
from map_locations_ai.processors.enrichment_processor import EnrichmentProcessor

# Initialize enrichment processor with enhanced error recovery
enrichment = EnrichmentProcessor("map_locations_ai/config.yaml")

# Process with improved error handling
try:
    enriched_locations = enrichment.process_locations(locations)
    print(f"✅ Successfully enriched {len(enriched_locations)} locations")
except Exception as e:
    print(f"⚠️ Enrichment failed: {e}")
    # Fallback to original locations
    enriched_locations = locations
```

## Available Functions

### Data Loading and Validation
- `load_locations_from_yaml(yaml_path: str) -> List[Location]`
- `create_sample_locations() -> List[Location]`
- `validate_location_data(locations: List[Location]) -> Dict[str, List[str]]`

### Data Analysis
- `get_location_summary(locations: List[Location]) -> Dict[str, Any]`
- `get_available_types(locations: List[Location]) -> List[str]`
- `get_available_tags(locations: List[Location]) -> List[str]`
- `get_available_neighborhoods(locations: List[Location]) -> List[str]`

### Filtering
- `filter_locations_by_type(locations: List[Location], types: List[str]) -> List[Location]`
- `filter_locations_by_tags(locations: List[Location], tags: List[str]) -> List[Location]`
- `filter_locations_by_neighborhood(locations: List[Location], neighborhoods: List[str]) -> List[Location]`

### Visualization
- `show_locations_grouped(locations: List[Location], group_by: str = "type", map_filename: str = "map.html", mobile: bool = False)`
- `show_locations_with_filtering(locations: List[Location], map_filename: str = "map.html", mobile: bool = False)`
- `show_locations_with_google_maps(locations: List[Location], map_filename: str = "map.html", mobile: bool = False)`

### Export
- `export_to_json(locations: List[Location], output_path: str)`
- `export_to_csv(locations: List[Location], output_path: str)`
- `export_to_geojson(locations: List[Location], output_path: str)`
- `export_to_kml(locations: List[Location], output_path: str)`
- `export_to_all_formats(locations: List[Location], base_path: str)`

### AI Processing
- `LocationExtractionPipeline(config_path: str)` - Main AI processing pipeline
- `Deduplicator(config_path: str)` - Smart deduplication
- `URLProcessor(config_path: str)` - URL processing and web scraping
- `GeocodingService(config_path: str)` - LLM-assisted geocoding

## Common Workflows

### 1. Data Exploration

```python
from map_locations import load_locations_from_yaml, get_location_summary

locations = load_locations_from_yaml("data.yaml")
summary = get_location_summary(locations)
print(f"Dataset contains {summary['total_count']} locations")
print(f"Types: {summary['types']}")
print(f"Top types: {dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:5])}")
```

### 2. Data Validation

```python
from map_locations import validate_location_data

issues = validate_location_data(locations)
if any(issues.values()):
    print("Data validation issues found:")
    for category, problems in issues.items():
        if problems:
            print(f"  {category}: {problems}")
else:
    print("✅ Data validation passed")
```

### 3. Filtered Analysis

```python
from map_locations import filter_locations_by_type, filter_locations_by_tags

# Get all food-related locations
food_locations = filter_locations_by_type(locations, ["restaurant", "cafe", "bar"])

# Get all historic sites
historic_sites = filter_locations_by_tags(locations, ["historic"])

# Create maps for each category
show_locations_grouped(food_locations, "food_map.html")
show_locations_grouped(historic_sites, "historic_map.html")

# Create mobile-optimized versions
show_locations_grouped(food_locations, "mobile_food_map.html", mobile=True)
show_locations_grouped(historic_sites, "mobile_historic_map.html", mobile=True)
```

### 4. AI Processing Workflow

```python
from map_locations_ai.pipeline import LocationExtractionPipeline

# Initialize pipeline
pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")

# Process with URL exploration
result = pipeline.process_file_with_urls("input.txt")
print(f"Extracted {result['total_locations']} locations")

# Process with deduplication
result = pipeline.process_file_with_deduplication("input.txt")
print(f"Final locations after deduplication: {result['total_locations']}")

# Complete workflow with geocoding
result = pipeline.process_file_with_urls_and_deduplication("input.txt")
print(f"Complete processing: {result['total_locations']} unique locations")
if 'geocoding_stats' in result:
    print(f"Geocoding: {result['geocoding_stats']['llm_geocoding_successes']} successful")
```

### 5. Complete Workflow

```python
from map_locations import (
    load_locations_from_yaml,
    validate_location_data,
    get_location_summary,
    filter_locations_by_type,
    show_locations_grouped,
    export_to_all_formats,
)
from map_locations_ai.pipeline import LocationExtractionPipeline

# AI extraction
pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
result = pipeline.process_file_with_urls_and_deduplication("input.txt")

# Load and validate
locations = load_locations_from_yaml("map_locations_ai/temp/merged.yaml")
issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Data has issues, please fix before proceeding")
    exit(1)

# Analyze
summary = get_location_summary(locations)
print(f"✅ Loaded {summary['total_count']} valid locations")

# Filter and visualize
museums = filter_locations_by_type(locations, ["museum", "gallery"])
show_locations_grouped(museums, "museums_map.html")
show_locations_grouped(museums, "mobile_museums_map.html", mobile=True)

# Export
export_to_all_formats(locations, "exports/complete_dataset")
print("✅ All exports completed")
```

## Data Validation

The `validate_location_data` function returns a dictionary with validation issues:

```python
{
    "missing_required": ["Location 'Eiffel Tower' missing required field 'type'"],
    "invalid_coordinates": ["Location 'Invalid Place' has coordinates outside valid range"],
    "invalid_dates": ["Location 'Old Place' has invalid date format"],
    "duplicate_names": ["Location 'Duplicate Name' appears multiple times"]
}
```

### Validation Categories

- **missing_required**: Locations missing required fields (name, type, latitude, longitude)
- **invalid_coordinates**: Coordinates outside valid ranges (lat: -90 to 90, lon: -180 to 180)
- **invalid_dates**: Date fields with invalid format (should be YYYY-MM-DD)
- **duplicate_names**: Multiple locations with the same name

## Error Handling

### Common Error Patterns

```python
from map_locations import load_locations_from_yaml, validate_location_data
import sys

try:
    # Load data
    locations = load_locations_from_yaml("locations.yaml")

    # Validate
    issues = validate_location_data(locations)
    if any(issues.values()):
        print("❌ Validation failed:")
        for category, problems in issues.items():
            if problems:
                print(f"  {category}: {len(problems)} issues")
        sys.exit(1)

    # Process data
    summary = get_location_summary(locations)
    print(f"✅ Successfully processed {summary['total_count']} locations")

except FileNotFoundError:
    print("❌ File not found: locations.yaml")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)
```

### AI Processing Error Handling

```python
from map_locations_ai.pipeline import LocationExtractionPipeline

def safe_ai_processing(input_file: str, config_file: str) -> Dict[str, Any]:
    """Safely process text with AI extraction."""
    try:
        pipeline = LocationExtractionPipeline(config_file)
        result = pipeline.process_file_with_urls_and_deduplication(input_file)

        print(f"✅ Extracted {result['total_locations']} locations")
        print(f"📊 Processed {result['total_chunks']} chunks")
        print(f"📝 Trace file: {result['trace_file']}")

        if 'geocoding_stats' in result:
            stats = result['geocoding_stats']
            print(f"🗺️ Geocoding: {stats['llm_geocoding_successes']}/{stats['llm_geocoding_attempts']} successful")

        return result
    except Exception as e:
        print(f"❌ AI processing failed: {e}")
        return {"error": str(e)}
```

### Graceful Degradation

```python
from map_locations import load_locations_from_yaml, filter_locations_by_type

# Load data with fallback
try:
    locations = load_locations_from_yaml("user_data.yaml")
except FileNotFoundError:
    print("⚠️ User data not found, using sample data")
    locations = create_sample_locations()

# Filter with error handling
try:
    restaurants = filter_locations_by_type(locations, ["restaurant"])
    if not restaurants:
        print("⚠️ No restaurants found, showing all locations")
        restaurants = locations
except Exception as e:
    print(f"⚠️ Error filtering locations: {e}")
    restaurants = locations
```

## Best Practices

### 1. Always Validate Data

```python
# Good practice
locations = load_locations_from_yaml("data.yaml")
issues = validate_location_data(locations)
if issues['missing_required']:
    print("❌ Cannot proceed with invalid data")
    return

# Process validated data
summary = get_location_summary(locations)
```

### 2. Use Type Hints

```python
from typing import List, Dict, Any
from map_locations import Location

def process_locations(locations: List[Location]) -> Dict[str, Any]:
    """Process locations with proper type hints."""
    return get_location_summary(locations)
```

### 3. Handle Edge Cases

```python
def safe_filter_locations(locations: List[Location], types: List[str]) -> List[Location]:
    """Safely filter locations with error handling."""
    if not locations:
        return []

    if not types:
        return locations

    try:
        return filter_locations_by_type(locations, types)
    except Exception as e:
        print(f"⚠️ Error filtering: {e}")
        return locations
```

### 4. Provide Meaningful Output

```python
def create_location_report(locations: List[Location]) -> str:
    """Create a human-readable report."""
    summary = get_location_summary(locations)

    report = f"""
Location Report
==============
Total Locations: {summary['total_count']}
Types: {', '.join(summary['types'])}
Top Types: {dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:3])}
Neighborhoods: {len(summary['neighborhoods'])}
Tags: {len(summary['tags'])}
"""
    return report
```

### 5. Use Consistent Naming

```python
# Good: Clear, descriptive names
restaurant_locations = filter_locations_by_type(locations, ["restaurant", "cafe"])
historic_sites = filter_locations_by_tags(locations, ["historic", "landmark"])

# Good: Consistent file naming
show_locations_grouped(restaurant_locations, "restaurants_map.html")
show_locations_grouped(historic_sites, "historic_sites_map.html")

# Good: Mobile versions
show_locations_grouped(restaurant_locations, "mobile_restaurants_map.html", mobile=True)
show_locations_grouped(historic_sites, "mobile_historic_sites_map.html", mobile=True)
```

### 6. AI Processing Best Practices

```python
from map_locations_ai.pipeline import LocationExtractionPipeline

def robust_ai_processing(input_file: str, config_file: str) -> Dict[str, Any]:
    """Robust AI processing with comprehensive error handling."""
    result = {"success": False, "output_files": [], "errors": []}

    try:
        # Initialize pipeline
        pipeline = LocationExtractionPipeline(config_file)

        # Process with all features
        result_data = pipeline.process_file_with_urls_and_deduplication(input_file)

        result["success"] = True
        result["total_locations"] = result_data["total_locations"]
        result["total_chunks"] = result_data["total_chunks"]
        result["trace_file"] = result_data["trace_file"]
        result["output_files"].append("map_locations_ai/temp/merged.yaml")

        # Include geocoding stats if available
        if 'geocoding_stats' in result_data:
            result["geocoding_stats"] = result_data["geocoding_stats"]

        print(f"✅ Successfully extracted {result_data['total_locations']} locations")

    except Exception as e:
        result["errors"].append(f"AI processing error: {e}")
        print(f"❌ AI processing failed: {e}")

    return result
```

### 7. Mobile Optimization Best Practices

```python
def create_responsive_maps(locations: List[Location], base_name: str) -> Dict[str, str]:
    """Create both desktop and mobile versions of maps."""
    maps = {}

    # Desktop version
    maps['desktop'] = show_locations_grouped(
        locations,
        map_filename=f"{base_name}_desktop.html",
        mobile=False
    )

    # Mobile version
    maps['mobile'] = show_locations_grouped(
        locations,
        map_filename=f"{base_name}_mobile.html",
        mobile=True
    )

    return maps
```

## Advanced Patterns

### Batch Processing

```python
def process_multiple_datasets(file_paths: List[str]) -> Dict[str, Any]:
    """Process multiple location datasets."""
    results = {}

    for file_path in file_paths:
        try:
            locations = load_locations_from_yaml(file_path)
            summary = get_location_summary(locations)
            results[file_path] = summary
        except Exception as e:
            results[file_path] = {"error": str(e)}

    return results
```

### Conditional Processing

```python
def smart_location_processing(locations: List[Location]) -> str:
    """Intelligently process locations based on content."""
    summary = get_location_summary(locations)

    if summary['total_count'] == 0:
        return "No locations to process"

    if len(summary['types']) == 1:
        # Single type - create simple map
        return show_locations_grouped(locations, "simple_map.html")

    if summary['total_count'] > 100:
        # Large dataset - create filtered views
        top_types = dict(sorted(summary['type_counts'].items(), key=lambda x: x[1], reverse=True)[:3])
        for location_type in top_types:
            filtered = filter_locations_by_type(locations, [location_type])
            show_locations_grouped(filtered, f"{location_type}_map.html")
            show_locations_grouped(filtered, f"mobile_{location_type}_map.html", mobile=True)
        return "Created filtered maps for top types"

    # Default - create comprehensive map
    return show_locations_grouped(locations, "comprehensive_map.html")
```

### Error Recovery

```python
def robust_location_processing(locations: List[Location]) -> Dict[str, Any]:
    """Process locations with comprehensive error handling."""
    result = {"success": False, "output_files": [], "errors": []}

    try:
        # Validate
        issues = validate_location_data(locations)
        if issues['missing_required']:
            result["errors"].extend(issues['missing_required'])
            return result

        # Create main map
        main_map = show_locations_grouped(locations, "main_map.html")
        result["output_files"].append(main_map)

        # Create mobile map
        mobile_map = show_locations_grouped(locations, "mobile_main_map.html", mobile=True)
        result["output_files"].append(mobile_map)

        # Export data
        export_to_all_formats(locations, "exports/")
        result["output_files"].extend([
            "exports/locations.json",
            "exports/locations.csv",
            "exports/locations.geojson",
            "exports/locations.kml"
        ])

        result["success"] = True

    except Exception as e:
        result["errors"].append(f"Processing error: {e}")

    return result
```

### AI Pipeline Integration

```python
def complete_ai_workflow(input_file: str, config_file: str) -> Dict[str, Any]:
    """Complete AI workflow from text to maps."""
    workflow_result = {
        "input_file": input_file,
        "extraction_success": False,
        "validation_success": False,
        "mapping_success": False,
        "output_files": [],
        "errors": []
    }

    try:
        # Step 1: AI Extraction
        pipeline = LocationExtractionPipeline(config_file)
        extraction_result = pipeline.process_file_with_urls_and_deduplication(input_file)
        workflow_result["extraction_success"] = True
        workflow_result["total_locations"] = extraction_result["total_locations"]

        # Step 2: Load and Validate
        locations = load_locations_from_yaml("map_locations_ai/temp/merged.yaml")
        issues = validate_location_data(locations)
        if not any(issues.values()):
            workflow_result["validation_success"] = True

        # Step 3: Create Maps
        map_file = show_locations_grouped(locations, "ai_extracted_map.html")
        mobile_map_file = show_locations_grouped(locations, "mobile_ai_extracted_map.html", mobile=True)
        workflow_result["mapping_success"] = True
        workflow_result["output_files"].extend([map_file, mobile_map_file])

        # Step 4: Export
        export_to_all_formats(locations, "exports/ai_locations")
        workflow_result["output_files"].extend([
            "exports/ai_locations.json",
            "exports/ai_locations.csv",
            "exports/ai_locations.geojson",
            "exports/ai_locations.kml"
        ])

        print(f"✅ Complete workflow: {extraction_result['total_locations']} locations processed")

    except Exception as e:
        workflow_result["errors"].append(f"Workflow error: {e}")
        print(f"❌ Workflow failed: {e}")

    return workflow_result
```
