"""
Location Converter Processor for the Map Locations AI pipeline.

Converts enriched location data to match the Location model exactly.
"""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from map_locations.common.formats import validate_locations
from map_locations.common.models import Location


class LocationConverter:
    """Converts enriched location data to Location model compliance."""

    def __init__(self) -> None:
        """Initialize the location converter."""
        pass

    def convert_to_location_model(
        self, enriched_locations: List[Dict[str, Any]]
    ) -> List[Location]:
        """
        Convert enriched locations to Location model format.

        Args:
            enriched_locations: List of enriched location dictionaries

        Returns:
            List of Location-compliant dictionaries
        """
        converted_locations = []

        for location in enriched_locations:
            converted = self._convert_single_location(location)
            converted_locations.append(converted)

        return converted_locations

    def _convert_single_location(self, location: Dict[str, Any]) -> Location:
        """
        Convert a single enriched location to Location model format.

        Args:
            location: Enriched location dictionary

        Returns:
            Location-compliant dictionary
        """
        # Start with required fields
        converted: Location = {
            "name": str(location.get("name", "")),
            "type": str(location.get("type", "")),
            "latitude": float(location.get("latitude", 0.0)),
            "longitude": float(location.get("longitude", 0.0)),
        }

        # Add optional fields with proper defaults
        optional_fields = {
            "address": "",
            "tags": [],
            "neighborhood": "",
            "date_added": "",
            "date_of_visit": "",
            "description": "",
            "official_website": "",
            "booking_url": "",
            "reviews_url": "",
            "opening_hours": "",
            "price_range": "",
            "duration_recommended": "",
            "best_time_to_visit": "",
            "accessibility_info": "",
            "nearby_attractions": [],
            "data_sources": [],
            "confidence_score": 0.0,
            "last_updated": "",
            "validation_status": "",
        }

        # Copy existing optional fields or use defaults
        for field, default_value in optional_fields.items():
            if field in location:
                converted[field] = location[field]  # type: ignore
            else:
                converted[field] = default_value  # type: ignore

        # Ensure proper data types
        converted["tags"] = self._ensure_list(converted["tags"])
        converted["nearby_attractions"] = self._ensure_list(
            converted["nearby_attractions"]
        )
        converted["data_sources"] = self._ensure_list(converted["data_sources"])
        converted["confidence_score"] = float(converted["confidence_score"])

        # Set metadata if missing
        if not converted["last_updated"]:
            converted["last_updated"] = datetime.now(timezone.utc).isoformat()

        if not converted["data_sources"]:
            converted["data_sources"] = ["web_search_enrichment"]

        if not converted["validation_status"]:
            converted["validation_status"] = "web_verified"

        if converted["confidence_score"] == 0.0:
            converted["confidence_score"] = 0.85

        # Clean up URLs - remove placeholder URLs
        converted = self._clean_urls(converted)

        # Cast to Location type to satisfy mypy
        return converted  # type: ignore

    def _ensure_list(self, value: Any) -> List[str]:
        """Ensure a value is a list of strings."""
        if isinstance(value, list):
            return [str(item) for item in value]
        elif value:
            return [str(value)]
        else:
            return []

    def _clean_urls(self, location: Location) -> Location:
        """Clean up URLs to remove placeholders and invalid URLs."""
        url_fields = ["official_website", "booking_url", "reviews_url"]

        for field in url_fields:
            url = location.get(field, "")
            # Remove any URL that looks fake or placeholder
            if url and (
                str(url).startswith("https://...")
                or str(url).startswith("http://...")
                or "example.com" in str(url)
                or "placeholder" in str(url).lower()
                or not self._is_valid_url(str(url))
                or self._looks_fake(str(url))
            ):
                location[field] = ""  # type: ignore

        return location

    def _looks_fake(self, url: str) -> bool:
        """Check if a URL looks fake or generated."""
        fake_indicators = [
            "example.com",
            "placeholder",
            "test",
            "mock",
            "fake",
            "dummy",
            "sample",
            "demo",
        ]

        url_lower = url.lower()
        return any(indicator in url_lower for indicator in fake_indicators)

    def _is_valid_url(self, url: str) -> bool:
        """Check if a URL is valid."""
        if not url:
            return False

        # Basic URL validation
        url_pattern = re.compile(
            r"^https?://"  # http:// or https://
            r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|"  # domain...
            r"localhost|"  # localhost...
            r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
            r"(?::\d+)?"  # optional port
            r"(?:/?|[/?]\S+)$",
            re.IGNORECASE,
        )

        return bool(url_pattern.match(url))

    def _validate_location(self, location: Location) -> Dict[str, Any]:
        """
        Validate a location against the Location model.

        Args:
            location: Location to validate

        Returns:
            Validation results
        """
        errors = []
        warnings = []

        # Check required fields
        required_fields = ["name", "type", "latitude", "longitude"]
        for field in required_fields:
            if field not in location or not location[field]:  # type: ignore
                errors.append(f"Missing required field: {field}")

        # Check coordinate validity
        lat = location.get("latitude", 0)
        lon = location.get("longitude", 0)
        if lat == 0 and lon == 0:
            warnings.append("Coordinates are set to 0,0 (unknown location)")
        elif not (-90 <= lat <= 90):
            errors.append(f"Invalid latitude: {lat}")
        elif not (-180 <= lon <= 180):
            errors.append(f"Invalid longitude: {lon}")

        # Check URL validity
        url_fields = ["official_website", "booking_url", "reviews_url"]
        for field in url_fields:
            url = location.get(field, "")
            if url and not self._is_valid_url(str(url)):
                warnings.append(f"Invalid URL in {field}: {url}")

        # Check confidence score
        confidence = location.get("confidence_score", 0)
        if not (0 <= confidence <= 1):
            errors.append(f"Invalid confidence score: {confidence}")

        return {"is_valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    def get_conversion_statistics(self, locations: List[Location]) -> Dict[str, Any]:
        """
        Get statistics about the conversion process.

        Args:
            locations: List of converted locations

        Returns:
            Conversion statistics
        """
        total = len(locations)

        # Count locations with various attributes
        with_coordinates = len(
            [
                loc
                for loc in locations
                if loc.get("latitude", 0) != 0 or loc.get("longitude", 0) != 0
            ]
        )
        with_websites = len(
            [loc for loc in locations if loc.get("official_website", "")]
        )
        with_descriptions = len(
            [loc for loc in locations if loc.get("description", "")]
        )
        with_hours = len([loc for loc in locations if loc.get("opening_hours", "")])

        # Validation results
        validation_results = []
        for location in locations:
            validation = self._validate_location(location)
            validation_results.append(validation)

        valid_locations = len([r for r in validation_results if r["is_valid"]])
        total_errors = sum(len(r["errors"]) for r in validation_results)
        total_warnings = sum(len(r["warnings"]) for r in validation_results)

        return {
            "total_locations": total,
            "valid_locations": valid_locations,
            "with_coordinates": with_coordinates,
            "with_websites": with_websites,
            "with_descriptions": with_descriptions,
            "with_hours": with_hours,
            "coordinate_coverage": (
                round(100 * with_coordinates / total, 1) if total > 0 else 0
            ),
            "website_coverage": (
                round(100 * with_websites / total, 1) if total > 0 else 0
            ),
            "description_coverage": (
                round(100 * with_descriptions / total, 1) if total > 0 else 0
            ),
            "hours_coverage": round(100 * with_hours / total, 1) if total > 0 else 0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "validation_rate": (
                round(100 * valid_locations / total, 1) if total > 0 else 0
            ),
        }
