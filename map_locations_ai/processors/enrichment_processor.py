"""
Simplified Location Enrichment Processor for the Map Locations AI pipeline.

Enriches basic extracted locations with comprehensive data using OpenAI responses API with web search.
"""

import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Optional

from openai import OpenAI


class EnrichmentProcessor:
    """Simplified enrichment processor using OpenAI responses API with web search."""

    def __init__(
        self,
        client: Optional[OpenAI],
        model: str = "gpt-4o-mini",
        max_searches_per_location: int = 3,
        timeout: int = 120,
        trace_manager=None,
        max_retries: int = 2,
        max_concurrent_calls: int = 5,
    ):
        """
        Initialize the enrichment processor.

        Args:
            client: OpenAI client instance (None for testing)
            model: OpenAI model to use
            max_searches_per_location: Maximum search operations per location
            timeout: Request timeout in seconds
            trace_manager: Optional trace manager for logging
            max_retries: Maximum number of retries for JSON parsing failures
            max_concurrent_calls: Maximum number of concurrent API calls
        """
        # Handle client tracking - the client might already be tracked by the pipeline
        if client is None:
            self.client = None
        elif hasattr(client, "usage_tracker"):
            # Client is already tracked (from pipeline)
            self.client = client
        else:
            # Client needs tracking - wrap it
            from .llm_processor import TrackedOpenAI

            tracked_client = TrackedOpenAI(api_key=client.api_key)
            tracked_client._original_responses = client.responses
            self.client = tracked_client

        self.model = model
        self.max_searches_per_location = max_searches_per_location
        self.timeout = timeout
        self.trace_manager = trace_manager
        self.max_retries = max_retries
        self.max_concurrent_calls = max_concurrent_calls

        # Statistics tracking
        self.stats = {
            "total_locations_processed": 0,
            "successful_enrichments": 0,
            "failed_enrichments": 0,
            "total_api_calls": 0,
            "total_retry_attempts": 0,
        }

    def enrich_locations(self, locations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich all locations with comprehensive data using concurrent processing.

        Args:
            locations: List of basic location dictionaries

        Returns:
            List of enriched location dictionaries
        """
        if not locations or not self.client:
            return locations

        print(
            f"🔍 Enriching {len(locations)} locations with max {self.max_concurrent_calls} concurrent calls..."
        )

        # Reset statistics
        self.stats = {
            "total_locations_processed": len(locations),
            "successful_enrichments": 0,
            "failed_enrichments": 0,
            "total_api_calls": 0,
            "total_retry_attempts": 0,
        }

        enriched_locations = []

        # Process locations with concurrent calls
        with ThreadPoolExecutor(max_workers=self.max_concurrent_calls) as executor:
            # Submit all enrichment tasks
            future_to_location = {
                executor.submit(self._enrich_single_location, location): location
                for location in locations
            }

            # Collect results as they complete
            for future in as_completed(future_to_location):
                location = future_to_location[future]
                try:
                    enriched_location = future.result()
                    enriched_locations.append(enriched_location)
                    self.stats["successful_enrichments"] += 1
                except Exception as e:
                    print(
                        f"❌ Failed to enrich location '{location.get('name', 'Unknown')}': {e}"
                    )
                    # Keep original location if enrichment fails
                    enriched_locations.append(location)
                    self.stats["failed_enrichments"] += 1

        print(
            f"✅ Enrichment complete: {self.stats['successful_enrichments']}/{len(locations)} successful"
        )
        return enriched_locations

    def _enrich_single_location(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich a single location using the OpenAI responses API.

        Args:
            location: Basic location dictionary

        Returns:
            Enriched location dictionary
        """
        if not self.client:
            print(
                f"⚠️ No OpenAI client available for location '{location.get('name', 'Unknown')}'"
            )
            return self._add_minimal_enrichment(location)

        try:
            # Create the system prompt
            system_prompt = self._get_system_prompt()

            # Create the input prompt
            input_prompt = self._create_input_prompt(location)

            # Make the API call with tracking parameters
            response = self.client.responses.create(
                model=self.model,
                tools=[{"type": "web_search_preview"}],
                instructions=system_prompt,
                input=input_prompt,
                timeout=self.timeout,
                calling_module="EnrichmentProcessor",
                operation_type="enrichment",
                retry_count=0,
            )

            self.stats["total_api_calls"] += 1

            # Parse the response
            enriched_location = self._parse_response(response, location)
            return enriched_location

        except Exception as e:
            print(
                f"❌ Error enriching location '{location.get('name', 'Unknown')}': {e}"
            )
            # Return original location with minimal enrichment
            return self._add_minimal_enrichment(location)

    def _get_system_prompt(self) -> str:
        """Get the system prompt for location enrichment."""
        return """You are a location data extraction specialist. Your task is to extract structured information about locations from web content.

CRITICAL: You must return ONLY valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.

LOCATION TYPE STANDARDIZATION:
Use these standardized location types (prefer American English spellings):

FOOD & DRINK (Red): restaurant, cafe, bar, pub
CULTURE & ARTS (Light Blue): museum, gallery, art gallery, theater, cinema, exhibition, studio tour
NATURE & OUTDOORS (Green): park, garden, botanical garden, cemetery
SHOPPING & COMMERCE (Blue): shopping, store, market, shopping center, shopping street, covered passage
ACCOMMODATION (Light Gray): hotel, accommodation, apartment
TRANSPORT (Gray): transport, station, metro station
LANDMARKS & MONUMENTS (Orange): landmark, monument, church, temple, basilica, palace, bridge
ENTERTAINMENT & EXPERIENCES (Purple): entertainment, theme park, amusement park, experience
NEIGHBORHOODS & AREAS (Dark Red): neighborhood, district, theater district
STREETS & URBAN (Dark Gray): street

Given web content about a location, extract the following information and return it as a valid JSON object:

{
    "name": "Official/correct name of the location",
    "type": "location type (museum, landmark, hotel, restaurant, etc.)",
    "latitude": 0.0,
    "longitude": 0.0,
    "address": "Full address of the location",
    "description": "Comprehensive tourist-friendly description",
    "official_website": "https://full-url-here.com",
    "booking_url": "https://full-booking-url.com",
    "reviews_url": "https://full-reviews-url.com",
    "opening_hours": "real opening hours as text",
    "price_range": "in $",
    "duration_recommended": "the number of hours as a float)",
    "best_time_to_visit": "Morning or late afternoon",
    "accessibility_info": "Wheelchair accessible",
    "nearby_attractions": ["Attraction 1", "Attraction 2"],
    "neighborhood": "Area name",
    "tags": ["tag1", "tag2"],
    "confidence_score": 0.85,
    "data_sources": [websites that were accessed to extract the information. stop at 10],
    "validation_status": "web_verified (only if the information was verified from the web)" or "unverified"
}

IMPORTANT REQUIREMENTS:
- Extract REAL coordinates if mentioned in the content (don't use 0.0 unless truly unknown)
- Extract FULL ADDRESS if mentioned in the content
- ONLY include URLs that are EXPLICITLY mentioned in the content
- NEVER generate fake or placeholder URLs
- Extract coordinates from content or use geocoding if mentioned
- Provide tourist-friendly descriptions based on actual content
- Include official websites ONLY if explicitly mentioned in content
- Make opening hours realistic based on content
- Use appropriate price ranges ($, $$, $$$)
- Keep descriptions informative but concise
- Only return valid JSON - no markdown, no explanations
- If information is not available in the content, use reasonable defaults
- Leave URL fields empty if no real URLs found in content
- Ensure all string values are properly quoted
- Use empty string "" for missing optional fields
- Use standardized location types to reduce synonyms"""

    def _create_input_prompt(self, location: Dict[str, Any]) -> str:
        """Create the input prompt for location enrichment."""
        return f"""Use the following information to provide an enriched json object with full information using your memory and assisted by the websearch tool.
Prefer found information over remembered information as things may have changed.

name:
    {location.get('name', '')}

description:
    {location.get('description', '')}

is_url:
    {location.get('is_url', False)}

source_text:
    {location.get('source_text', '')}

likely-type:
    {location.get('type', '')}

url:
    {location.get('url', '')}

EXTRACTION REQUIREMENTS:
Extract all available information and return a complete JSON object that matches the Location model in the system prompt.

TYPE STANDARDIZATION - CONSOLIDATE SYNONYMS:
FOOD & DRINK:
- Use "restaurant" for: dining, eatery, food establishment, bistro, restaurant
- Use "cafe" for: cafe, coffee shop, tea room, coffeehouse
- Use "bar" for: bar, pub, tavern, cocktail bar, pub

CULTURE & ARTS:
- Use "museum" for: gallery (when art museum), exhibition space, art museum
- Use "gallery" for: art gallery, commercial gallery, art space
- Use "theater" for: theatre, theater, performance venue, playhouse (prefer American spelling)
- Use "cinema" for: movie theater, film theater, cinema
- Use "exhibition" for: exhibition space, gallery, art show
- Use "studio tour" for: studio visit, artist studio, workshop

NATURE & OUTDOORS:
- Use "park" for: green space, recreation area, public garden, park
- Use "garden" for: botanical garden, public garden, private garden
- Use "cemetery" for: graveyard, burial ground, memorial park

SHOPPING & COMMERCE:
- Use "shopping center" for: mall, shopping mall, plaza, shopping complex
- Use "market" for: shopping area, bazaar, marketplace, market
- Use "covered passage" for: passage, covered passage, passage couvert, galleria, arcade, shopping arcade
- Use "shopping street" for: shopping district, retail street, commercial street

ACCOMMODATION:
- Use "hotel" for: lodging, accommodation, inn, guesthouse, hotel
- Use "apartment" for: apartment, flat, rental unit, condo

TRANSPORT:
- Use "metro station" for: subway, underground, train station, tube station, metro station
- Use "station" for: train station, bus station, transport hub

LANDMARKS & MONUMENTS:
- Use "landmark" for: attraction, site, place, venue, point of interest, tourist attraction
- Use "monument" for: memorial, statue, monument
- Use "church" for: cathedral, chapel, church, basilica
- Use "temple" for: temple, shrine, religious site
- Use "palace" for: palace, castle, royal residence
- Use "bridge" for: bridge, viaduct, crossing

ENTERTAINMENT & EXPERIENCES:
- Use "theme park" for: amusement park, theme park, entertainment park
- Use "entertainment" for: entertainment venue, entertainment center

NEIGHBORHOODS & AREAS:
- Use "neighborhood" for: area, district, quarter, arrondissement, neighborhood
- Use "theater district" for: theater district, entertainment district

CRITICAL REQUIREMENTS:
1. **Extract REAL coordinates** from content or use geocoding if location is mentioned
2. **Extract FULL ADDRESS** if mentioned in content
3. **ONLY include REAL URLs found in content** - never generate fake URLs
4. **Official name** and correct spelling from content
5. **Detailed description** based on actual web content
6. **Opening hours** if mentioned in content
7. **Official website** ONLY if explicitly mentioned in content
8. **Tourist information** like best times to visit, duration, etc.
9. **Include confidence_score** and validation_status
10. **Leave URL fields empty if no real URLs found in content**
11. **Use standardized location types** from the system prompt to reduce synonyms
12. **Consolidate synonyms** using the rules above - prefer American English spellings

Return ONLY the JSON object, no additional text."""

    def _parse_response(
        self, response: Any, original_location: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse the OpenAI response and merge with original location data.

        Args:
            response: OpenAI response object
            original_location: Original location data

        Returns:
            Enriched location dictionary
        """
        try:
            # Extract JSON from response
            response_text = response.output_text.strip()

            # Handle markdown code blocks (```json ... ```)
            if response_text.startswith("```json"):
                # Extract content between ```json and ```
                start_marker = "```json"
                end_marker = "```"
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.rfind(end_marker)
                if start_idx > 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()
            elif response_text.startswith("```"):
                # Extract content between ``` and ```
                start_marker = "```"
                end_marker = "```"
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.rfind(end_marker)
                if start_idx > 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()

            # Try to parse as JSON
            if response_text.startswith("{") and response_text.endswith("}"):
                enriched_data = json.loads(response_text)

                # Merge with original location data
                merged_location = original_location.copy()
                merged_location.update(enriched_data)

                # Ensure required fields are present
                merged_location = self._ensure_required_fields(merged_location)

                return merged_location
            else:
                print(
                    f"⚠️ Invalid JSON response for location '{original_location.get('name', 'Unknown')}'"
                )
                print(f"Response: {response_text}")
                return self._add_minimal_enrichment(original_location)

        except json.JSONDecodeError as e:
            print(
                f"⚠️ JSON parsing error for location '{original_location.get('name', 'Unknown')}': {e}"
            )
            print(f"Response: {response_text}")
            return self._add_minimal_enrichment(original_location)
        except Exception as e:
            print(
                f"⚠️ Response parsing error for location '{original_location.get('name', 'Unknown')}': {e}"
            )
            print(f"Response: {response_text}")
            return self._add_minimal_enrichment(original_location)

    def _ensure_required_fields(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all required fields are present in the location data."""
        required_fields = {
            "name": "",
            "type": "",
            "latitude": 0.0,
            "longitude": 0.0,
            "address": "",
            "description": "",
            "official_website": "",
            "booking_url": "",
            "reviews_url": "",
            "opening_hours": "",
            "price_range": "",
            "duration_recommended": 0.0,
            "best_time_to_visit": "",
            "accessibility_info": "",
            "nearby_attractions": [],
            "neighborhood": "",
            "tags": [],
            "confidence_score": 0.0,
            "data_sources": [],
            "validation_status": "unverified",
        }

        # Ensure all required fields exist
        for field, default_value in required_fields.items():
            if field not in location:
                location[field] = default_value

        return location

    def _add_minimal_enrichment(self, location: Dict[str, Any]) -> Dict[str, Any]:
        """Add minimal enrichment to a location when full enrichment fails."""
        enriched = location.copy()

        # Add basic fields if missing
        if "confidence_score" not in enriched:
            enriched["confidence_score"] = 0.5
        if "validation_status" not in enriched:
            enriched["validation_status"] = "unverified"
        if "data_sources" not in enriched:
            enriched["data_sources"] = []
        if "tags" not in enriched:
            enriched["tags"] = []
        if "nearby_attractions" not in enriched:
            enriched["nearby_attractions"] = []

        return enriched

    def get_enrichment_statistics(
        self, enriched_locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Get enrichment statistics."""
        if not enriched_locations:
            return {
                "coordinate_coverage": 0.0,
                "website_coverage": 0.0,
                "hours_coverage": 0.0,
                "total_locations": 0,
            }

        total = len(enriched_locations)
        coordinates_count = sum(
            1
            for loc in enriched_locations
            if loc.get("latitude", 0) != 0 or loc.get("longitude", 0) != 0
        )
        website_count = sum(
            1 for loc in enriched_locations if loc.get("official_website")
        )
        hours_count = sum(1 for loc in enriched_locations if loc.get("opening_hours"))

        return {
            "coordinate_coverage": (
                (coordinates_count / total) * 100 if total > 0 else 0.0
            ),
            "website_coverage": (website_count / total) * 100 if total > 0 else 0.0,
            "hours_coverage": (hours_count / total) * 100 if total > 0 else 0.0,
            "total_locations": total,
            "validation_statuses": {},  # Add empty validation_statuses to match file manager expectations
            "api_statistics": self.stats,
        }

    def get_retry_statistics(self) -> Dict[str, Any]:
        """Get retry statistics."""
        return {
            "total_locations_processed": self.stats["total_locations_processed"],
            "locations_with_retries": 0,  # Simplified version doesn't track retries
            "total_retry_attempts": self.stats["total_retry_attempts"],
            "successful_retries": 0,
            "failed_retries": 0,
        }

    def configure_rate_limiting(self, min_request_interval: float = 1.0):
        """Configure rate limiting (simplified - uses concurrent processing instead)."""
        print(
            f"⚙️ Rate limiting configured via concurrent processing (max {self.max_concurrent_calls} calls)"
        )

    def configure_rate_limiting_from_config(self, rate_limit_config: Dict[str, Any]):
        """Configure rate limiting from config (simplified)."""
        max_concurrent = rate_limit_config.get("max_concurrent_calls", 5)
        self.max_concurrent_calls = max_concurrent
        print(f"⚙️ Configured max concurrent calls: {self.max_concurrent_calls}")
