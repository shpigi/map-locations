"""
Main processing pipeline for location data extraction and enrichment.
"""

import re
from typing import Any, Dict, List, Optional

from map_locations.common import Location, LocationList

from .extractors import ExtractedLocation, TextExtractor, URLExtractor


def extract_urls_from_text(text: str) -> List[str]:
    """Extract URLs from text using regex."""
    url_pattern = r'https?://[^\s<>"\'()[\]{}]+'
    return re.findall(url_pattern, text)


def remove_urls_from_text(text: str) -> str:
    """Remove URLs from text to avoid duplicate processing."""
    url_pattern = r'https?://[^\s<>"\'()[\]{}]+'
    return re.sub(url_pattern, "", text)


class LocationPipeline:
    """
    Main pipeline for processing location data through extraction, enrichment, and validation.

    This pipeline coordinates the various stages of location data processing:
    1. Extract locations from input sources (text, URLs, etc.)
    2. Enrich locations with additional data from external sources
    3. Validate and score the accuracy of location data
    4. Output structured location data
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the location pipeline.

        Args:
            config: Optional configuration dictionary for pipeline settings
        """
        self.config = config or {}

        # Initialize extractors
        try:
            self.text_extractor: Optional[TextExtractor] = TextExtractor(config)
            self.url_extractor: Optional[URLExtractor] = URLExtractor(config)
        except ValueError as e:
            print(f"Warning: Could not initialize extractors: {e}")
            self.text_extractor = None
            self.url_extractor = None

        # Initialize enrichers and validators (to be implemented later)
        self.enrichers = None
        self.validators = None

    def process_text(self, text: str, region: Optional[str] = None) -> List[ExtractedLocation]:
        """
        Extract locations from text input.

        Args:
            text: Input text containing location mentions
            region: Optional region hint for better location resolution

        Returns:
            List of processed ExtractedLocation objects
        """
        if not self.text_extractor:
            print("TextExtractor not available - missing API key?")
            return []

        # First extract URLs from text and process them separately
        urls = extract_urls_from_text(text)
        text_without_urls = remove_urls_from_text(text)

        locations = []

        # Process text (without URLs)
        if text_without_urls.strip():
            text_locations = self.text_extractor.extract(text_without_urls, region)
            locations.extend(text_locations)

        # Process extracted URLs
        if urls:
            url_locations = self.process_urls(urls, region)
            locations.extend(url_locations)

        return locations

    def process_urls(
        self, urls: List[str], region: Optional[str] = None
    ) -> List[ExtractedLocation]:
        """
        Extract locations from web URLs.

        Args:
            urls: List of URLs to process
            region: Optional region hint for better location resolution

        Returns:
            List of processed ExtractedLocation objects
        """
        if not self.url_extractor:
            print("URLExtractor not available")
            return []

        return self.url_extractor.extract(urls, region)

    def process_mixed_input(
        self,
        text: Optional[str] = None,
        urls: Optional[List[str]] = None,
        region: Optional[str] = None,
    ) -> List[ExtractedLocation]:
        """
        Process mixed input sources (text and URLs).

        Args:
            text: Optional text input
            urls: Optional list of URLs
            region: Optional region hint

        Returns:
            Combined list of processed ExtractedLocation objects
        """
        locations = []

        if text:
            locations.extend(self.process_text(text, region))

        if urls:
            locations.extend(self.process_urls(urls, region))

        return locations

    def enrich_existing_locations(self, locations: LocationList) -> LocationList:
        """
        Enrich existing location data with additional information.

        Args:
            locations: List of existing Location objects to enrich

        Returns:
            List of enriched Location objects
        """
        # Placeholder implementation
        # TODO: Implement location enrichment
        return locations

    def validate_locations(self, locations: LocationList) -> LocationList:
        """
        Validate and score location data accuracy.

        Args:
            locations: List of Location objects to validate

        Returns:
            List of validated Location objects with confidence scores
        """
        # Placeholder implementation
        # TODO: Implement location validation
        return locations

    def extracted_to_locations(self, extracted: List[ExtractedLocation]) -> LocationList:
        """
        Convert ExtractedLocation objects to full Location objects.

        This is a basic conversion - full enrichment will be implemented later.

        Args:
            extracted: List of ExtractedLocation objects

        Returns:
            List of Location objects
        """
        locations = []

        for ext_loc in extracted:
            # Create a minimal Location object
            # Most fields will be filled by enrichment later
            location: Location = {
                "name": ext_loc.name,
                "type": "unknown",  # Will be determined by enrichment
                "latitude": 0.0,  # Will be geocoded later
                "longitude": 0.0,  # Will be geocoded later
                "confidence_score": ext_loc.confidence,
                "data_sources": [ext_loc.source_snippet_or_url or "text_extraction"],
            }

            # Add address hint if available
            if ext_loc.address_or_hint:
                location["neighborhood"] = ext_loc.address_or_hint

            locations.append(location)

        return locations
