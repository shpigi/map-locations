#!/bin/bash

# Map generation script for map_locations package
# Note: Advanced filtering (--advanced-filter) was removed from the CLI
# All maps now use the standard grouped view with layer controls

# Exit on any error
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create output directory if it doesn't exist
if [ ! -d "maps" ]; then
    print_status "Creating maps directory..."
    mkdir -p maps
fi

# Function to run map generation with error handling
generate_map() {
    local input_file="$1"
    local output_file="$2"
    local additional_args="$3"

    if [ ! -f "$input_file" ]; then
        print_error "Input file not found: $input_file"
        return 1
    fi

    print_status "Generating map: $output_file"
    python -m map_locations.cli "$input_file" --output "$output_file" $additional_args

    if [ $? -eq 0 ]; then
        print_status "✅ Successfully generated: $output_file"
    else
        print_error "❌ Failed to generate: $output_file"
        return 1
    fi
}

# Main execution
print_status "Starting map generation..."

# Paris maps
generate_map "map_locations_ai/temp/user_input_01_paris/deduplicated_locations.yaml" \
    "maps/user_input_01_paris_mobile.html" \
    "--tile-provider google_maps --mobile"

generate_map "map_locations_ai/temp/user_input_01_paris/deduplicated_locations.yaml" \
    "maps/user_input_01_paris.html" \
    "--tile-provider google_maps"

# London maps
generate_map "map_locations_ai/temp/user_input_01_london/deduplicated_locations.yaml" \
    "maps/user_input_01_london_mobile.html" \
    "--tile-provider google_maps --mobile"

generate_map "map_locations_ai/temp/user_input_01_london/deduplicated_locations.yaml" \
    "maps/user_input_01_london.html" \
    "--tile-provider google_maps"

# KML exports
generate_map "map_locations_ai/temp/user_input_01_paris/deduplicated_locations.yaml" \
    "maps/user_input_01_paris.kml" \
    "--format kml"

generate_map "map_locations_ai/temp/user_input_01_london/deduplicated_locations.yaml" \
    "maps/user_input_01_london.kml" \
    "--format kml"

# Mobile KML exports
generate_map "map_locations_ai/temp/user_input_01_paris/deduplicated_locations.yaml" \
    "maps/user_input_01_paris_mobile.kml" \
    "--format kml --mobile"

generate_map "map_locations_ai/temp/user_input_01_london/deduplicated_locations.yaml" \
    "maps/user_input_01_london_mobile.kml" \
    "--format kml --mobile"

print_status "🎉 All map generation completed successfully!"
