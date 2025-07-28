"""
Geocoding Service for the Map Locations AI pipeline.

Uses free geocoding services to get coordinates for locations.
"""

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
        llm_model: str = "gpt-4o-mini",
    ):
        """
        Initialize the geocoding service.

        Args:
            timeout: Request timeout in seconds
            rate_limit_delay: Delay between requests to respect rate limits
            llm_client: Optional OpenAI client for LLM-assisted geocoding
            llm_model: Model to use for LLM-assisted geocoding
        """
        self.timeout = timeout
        self.rate_limit_delay = rate_limit_delay
        self.llm_client = llm_client
        self.llm_model = llm_model
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "MapLocationsAI/1.0 (https://github.com/your-repo)"}
        )

    def geocode_location(
        self, location_name: str, location_type: str = "", city: str = "London"
    ) -> Optional[Tuple[float, float]]:
        """
        Geocode a location using Nominatim (OpenStreetMap).

        Args:
            location_name: Name of the location
            location_type: Type of location (optional)
            city: City context (default: London)

        Returns:
            Tuple of (latitude, longitude) or None if not found
        """
        try:
            # Try multiple search strategies
            search_queries = []

            # Strategy 1: Full query with city
            query_parts = [location_name]
            if location_type:
                query_parts.append(location_type)
            query_parts.append(city)
            search_queries.append(", ".join(query_parts))

            # Strategy 2: Just location name and city
            search_queries.append(f"{location_name}, {city}")

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

            print(f"    ❌ No coordinates found after trying all strategies")
            return None

        except Exception as e:
            print(f"    ⚠️ Geocoding error: {e}")
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
                    location.get("neighborhood", "London"),
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
