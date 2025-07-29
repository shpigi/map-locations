"""
Geocoding Service for the Map Locations AI pipeline.

Uses free geocoding services to get coordinates for locations.
"""

import json
import time
from typing import Any, Dict, List, Optional, Tuple

import requests


class GeocodingService:
    """Provides geocoding services using free APIs."""

    def __init__(
        self,
        timeout: int = 10,
        rate_limit_delay: float = 1.0,
        llm_client=None,
        model: str = "gpt-4o-mini",
    ):
        """
        Initialize the geocoding service.

        Args:
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests to respect rate limits
            llm_client: Optional OpenAI client for LLM-assisted geocoding
            model: Model to use for LLM-assisted geocoding
        """
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.llm_client = llm_client
        self.model = model
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MapLocationsAI/1.0 (https://github.com/your-repo)"}
        )

    def geocode_location(
        self, location_name: str, location_type: str = "", address: str = ""
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode a location using Nominatim (OpenStreetMap) with LLM fallback.

        Args:
            location_name: Name of the location
            location_type: Type of location (optional)
            address: Address context (optional)

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Try multiple search strategies with Nominatim
            search_queries = []

            # Strategy 1: Full query with address
            query_parts = [location_name]
            if location_type:
                query_parts.append(location_type)
            if address:
                query_parts.append(address)
            if query_parts:
                search_queries.append(", ".join(query_parts))

            # Strategy 2: Just location name and address
            if address:
                search_queries.append(f"{location_name}, {address}")

            # Strategy 3: Just location name (global search)
            search_queries.append(location_name)

            # Strategy 4: Location name with type (global search)
            if location_type:
                search_queries.append(f"{location_name} {location_type}")

            # Try each search strategy
            for search_query in search_queries:
                print(f"    🔍 Trying: {search_query}")

                # Use Nominatim API
                url = "https://nominatim.openstreetmap.org/search"
                params = {
                    "q": search_query,
                    "format": "json",
                    "limit": 1,
                    "addressdetails": 1,
                }

                response = self.session.get(url, params=params, timeout=self.timeout)

                if response.status_code == 200:
                    data = response.json()

                    if data:
                        result = data[0]
                        lat = float(result["lat"])
                        lon = float(result["lon"])

                        # Validate coordinates
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            print(f"    📍 Found coordinates: {lat}, {lon}")
                            return (lat, lon)
                        else:
                            print(f"    ⚠️ Invalid coordinates returned: {lat}, {lon}")
                    else:
                        print(f"    ❌ No results for: {search_query}")
                else:
                    print(f"    ❌ Request failed: {response.status_code}")

                # Rate limiting between attempts
                time.sleep(0.5)

            # LLM-assisted geocoding as last resort
            if self.llm_client:
                print(f"    🤖 Trying LLM-assisted geocoding...")
                coords = self._llm_geocode_location(
                    location_name, location_type, address
                )
                if coords:
                    return coords

            print(f"    ❌ No coordinates found after trying all strategies")
            return None

        except Exception as e:
            print(f"    ⚠️ Geocoding error: {e}")
            return None

    def _llm_geocode_location(
        self, location_name: str, location_type: str = "", address: str = ""
    ) -> Optional[Tuple[float, float]]:
        """
        Use LLM with web search to find coordinates for a location.

        Args:
            location_name: Name of the location
            location_type: Type of location (optional)
            address: Address context (optional)

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Create the system prompt
            system_prompt = """You are a geocoding specialist. Your task is to find the exact coordinates (latitude and longitude) for locations using web search.

CRITICAL: You must return ONLY valid JSON. Do not include any explanatory text, markdown formatting, or additional content outside the JSON object.

Return the coordinates in this exact JSON format:
{
    "latitude": Optional[float],
    "longitude": Optional[float],
    "confidence": float
}

IMPORTANT REQUIREMENTS:
- Use web search to find the exact coordinates
- Return coordinates in decimal degrees format
- Latitude range: -90 to 90
- Longitude range: -180 to 180
- Only return coordinates if you can find them with high confidence
- If coordinates cannot be found, return null
- Do not generate fake coordinates
- Use official sources when possible
- Include confidence score (0.0 to 1.0)
- Return ONLY valid JSON - no markdown, no explanations"""

            # Create the input prompt
            input_prompt = f"""Find the exact coordinates for this location using web search:

Location Name: {location_name}
Location Type: {location_type}
Location Address: {address}

Search for the exact address and coordinates of this location. Look for:
- Official website coordinates
- Google Maps listings
- Official tourism websites
- Government location databases

Return ONLY the JSON object with coordinates if found, or null if not found."""

            # Make the API call
            response = self.llm_client.responses.create(
                model=self.model,
                tools=[{"type": "web_search_preview"}],
                instructions=system_prompt,
                input=input_prompt,
                timeout=self.timeout,
                calling_module="GeocodingService",
                operation_type="llm_geocoding",
                retry_count=0,
            )

            # Parse the response
            response_text = response.output_text.strip()

            # Handle markdown code blocks
            if response_text.startswith("```json"):
                start_marker = "```json"
                end_marker = "```"
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.rfind(end_marker)
                if start_idx > 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()
            elif response_text.startswith("```"):
                start_marker = "```"
                end_marker = "```"
                start_idx = response_text.find(start_marker) + len(start_marker)
                end_idx = response_text.rfind(end_marker)
                if start_idx > 0 and end_idx > start_idx:
                    response_text = response_text[start_idx:end_idx].strip()

            # Try to parse as JSON
            if response_text.startswith("{") and response_text.endswith("}"):
                try:
                    data = json.loads(response_text)

                    # Check if coordinates are present and valid
                    lat = data.get("latitude")
                    lon = data.get("longitude")

                    if lat is not None and lon is not None:
                        lat = float(lat)
                        lon = float(lon)

                        # Validate coordinates
                        if -90 <= lat <= 90 and -180 <= lon <= 180:
                            confidence = data.get("confidence", 0.5)
                            print(
                                f"    📍 LLM found coordinates: {lat}, {lon} (confidence: {confidence})"
                            )
                            return (lat, lon)
                        else:
                            print(
                                f"    ⚠️ LLM returned invalid coordinates: {lat}, {lon}"
                            )
                    else:
                        print(f"    ❌ LLM response missing coordinates")

                except (json.JSONDecodeError, ValueError) as e:
                    print(f"    ⚠️ LLM response parsing error: {e}")
                    print(f"    Response: {response_text}")
            else:
                print(f"    ❌ LLM response not valid JSON")
                print(f"    Response: {response_text}")

            return None

        except Exception as e:
            print(f"    ⚠️ LLM geocoding error: {e}")
            return None

    def geocode_locations(
        self, locations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Geocode a list of locations.

        Args:
            locations: List of location dictionaries

        Returns:
            List of locations with updated coordinates
        """
        geocoded_locations = []

        for i, location in enumerate(locations, 1):
            print(
                f"  Geocoding location {i}/{len(locations)}: {location.get('name', 'Unknown')}"
            )

            # Check if coordinates are missing (0.0, 0.0)
            lat = location.get("latitude", 0.0)
            lon = location.get("longitude", 0.0)

            if lat == 0.0 and lon == 0.0:
                # Try to geocode
                coords = self.geocode_location(
                    location.get("name", ""),
                    location.get("type", ""),
                    location.get("address", ""),
                )

                if coords:
                    location["latitude"] = coords[0]
                    location["longitude"] = coords[1]
                    location["data_sources"] = location.get("data_sources", []) + [
                        "geocoding"
                    ]
                    print(f"    ✅ Coordinates updated")
                else:
                    print(f"    ❌ Could not find coordinates")
            else:
                print(f"    ⏭️ Coordinates already present: {lat}, {lon}")

            geocoded_locations.append(location)

            # Rate limiting
            if i < len(locations):
                time.sleep(self.rate_limit_delay)

        return geocoded_locations

    def get_geocoding_statistics(
        self, locations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Get statistics about geocoding results.

        Args:
            locations: List of geocoded locations

        Returns:
            Dictionary with geocoding statistics
        """
        total = len(locations)
        with_coordinates = 0
        geocoded_count = 0

        for location in locations:
            lat = location.get("latitude", 0.0)
            lon = location.get("longitude", 0.0)

            if lat != 0.0 or lon != 0.0:
                with_coordinates += 1

                # Check if geocoding was used
                data_sources = location.get("data_sources", [])
                if "geocoding" in data_sources:
                    geocoded_count += 1

        return {
            "total_locations": total,
            "with_coordinates": with_coordinates,
            "geocoded_count": geocoded_count,
            "coordinate_coverage": (
                round(100 * with_coordinates / total, 1) if total > 0 else 0
            ),
            "geocoding_success_rate": (
                round(100 * geocoded_count / total, 1) if total > 0 else 0
            ),
        }
