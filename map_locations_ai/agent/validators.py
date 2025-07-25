"""
Location validation and accuracy scoring components.

This module provides validators that check the accuracy and quality of location data,
assign confidence scores, and identify potential issues.
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse

import requests
from map_locations.common import Location, LocationList


class BaseValidator(ABC):
    """Base class for all location validators."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the validator with configuration.

        Args:
            config: Configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def validate(self, location: Location) -> Tuple[bool, float, str]:
        """
        Validate a single location.

        Args:
            location: Location to validate

        Returns:
            Tuple of (is_valid, confidence_score, validation_message)
        """
        pass


class CoordinateValidator(BaseValidator):
    """Validate location coordinates for accuracy and reasonableness."""

    def validate(self, location: Location) -> Tuple[bool, float, str]:
        """
        Validate location coordinates.

        Args:
            location: Location to validate

        Returns:
            Tuple of (is_valid, confidence_score, validation_message)
        """
        lat = location.get("latitude")
        lon = location.get("longitude")

        # Check if coordinates exist
        if lat is None or lon is None:
            return False, 0.0, "Missing coordinates"

        # Check coordinate ranges
        if not isinstance(lat, (int, float)) or not (-90 <= lat <= 90):
            return False, 0.0, f"Invalid latitude: {lat}"

        if not isinstance(lon, (int, float)) or not (-180 <= lon <= 180):
            return False, 0.0, f"Invalid longitude: {lon}"

        # Check for suspicious coordinates (e.g., 0,0 which is in the ocean)
        if lat == 0 and lon == 0:
            return False, 0.1, "Suspicious coordinates: 0,0"

        # TODO: Implement reverse geocoding validation
        # - Check if coordinates correspond to the named location
        # - Verify against multiple geocoding services

        return True, 0.9, "Coordinates appear valid"


class URLValidator(BaseValidator):
    """Validate URLs for accessibility and relevance."""

    def validate(self, location: Location) -> Tuple[bool, float, str]:
        """
        Validate URLs in location data.

        Args:
            location: Location to validate

        Returns:
            Tuple of (is_valid, confidence_score, validation_message)
        """
        url_fields = ["official_website", "booking_url", "reviews_url"]
        issues = []
        valid_urls = 0
        total_urls = 0

        for field in url_fields:
            url = location.get(field)
            if url:
                total_urls += 1
                is_valid, message = self._validate_single_url(url)
                if is_valid:
                    valid_urls += 1
                else:
                    issues.append(f"{field}: {message}")

        if total_urls == 0:
            return True, 0.5, "No URLs to validate"

        confidence = valid_urls / total_urls
        is_valid = confidence > 0.5

        if issues:
            message = f"URL issues: {'; '.join(issues)}"
        else:
            message = f"All {valid_urls} URLs are valid"

        return is_valid, confidence, message

    def _validate_single_url(self, url: str) -> Tuple[bool, str]:
        """
        Validate a single URL.

        Args:
            url: URL to validate

        Returns:
            Tuple of (is_valid, message)
        """
        # Check URL format
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False, "Invalid URL format"
        except Exception:
            return False, "Malformed URL"

        # Check if URL is accessible (with timeout)
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            if response.status_code == 200:
                return True, "URL accessible"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.RequestException as e:
            return False, f"Request failed: {str(e)[:50]}"


class ContentValidator(BaseValidator):
    """Validate location content for completeness and quality."""

    def validate(self, location: Location) -> Tuple[bool, float, str]:
        """
        Validate location content quality.

        Args:
            location: Location to validate

        Returns:
            Tuple of (is_valid, confidence_score, validation_message)
        """
        required_fields = ["name", "type", "latitude", "longitude"]
        optional_fields = ["description", "tags", "neighborhood", "official_website"]

        # Check required fields
        missing_required = [f for f in required_fields if not location.get(f)]
        if missing_required:
            return False, 0.0, f"Missing required fields: {missing_required}"

        # Calculate completeness score
        present_optional = len([f for f in optional_fields if location.get(f)])
        completeness = present_optional / len(optional_fields)

        # Check content quality
        quality_issues = []

        # Check name quality
        name = location.get("name", "")
        if len(name) < 3:
            quality_issues.append("Name too short")
        elif name.isupper() or name.islower():
            quality_issues.append("Name not properly capitalized")

        # Check description quality
        description = location.get("description", "")
        if description and len(description) < 20:
            quality_issues.append("Description too brief")

        # Calculate quality score
        quality_score = max(0.0, 1.0 - len(quality_issues) * 0.2)

        # Combined confidence score
        confidence = (completeness + quality_score) / 2

        is_valid = confidence > 0.3

        if quality_issues:
            message = (
                f"Quality issues: {'; '.join(quality_issues)}. Completeness: {completeness:.1%}"
            )
        else:
            message = f"Good quality content. Completeness: {completeness:.1%}"

        return is_valid, confidence, message


class CompositeValidator(BaseValidator):
    """Composite validator that runs multiple validation checks."""

    def __init__(self, validators: List[BaseValidator], config: Optional[Dict[str, Any]] = None):
        """
        Initialize composite validator.

        Args:
            validators: List of validators to use
            config: Configuration dictionary
        """
        super().__init__(config)
        self.validators = validators

    def validate(self, location: Location) -> Tuple[bool, float, str]:
        """
        Run all validators on a location.

        Args:
            location: Location to validate

        Returns:
            Tuple of (is_valid, overall_confidence_score, validation_summary)
        """
        results = []
        messages = []

        for validator in self.validators:
            try:
                is_valid, confidence, message = validator.validate(location)
                results.append((is_valid, confidence))
                messages.append(f"{validator.__class__.__name__}: {message}")
            except Exception as e:
                results.append((False, 0.0))
                messages.append(f"{validator.__class__.__name__}: Error - {e}")

        # Calculate overall scores
        valid_count = sum(1 for is_valid, _ in results if is_valid)
        total_count = len(results)
        overall_confidence = sum(conf for _, conf in results) / total_count

        is_overall_valid = valid_count >= total_count * 0.5

        summary = f"Passed {valid_count}/{total_count} validators. " + "; ".join(messages)

        return is_overall_valid, overall_confidence, summary

    def validate_batch(self, locations: LocationList) -> LocationList:
        """
        Validate multiple locations and add validation metadata.

        Args:
            locations: List of locations to validate

        Returns:
            List of locations with validation metadata added
        """
        validated_locations = []

        for location in locations:
            validated_location = location.copy()
            is_valid, confidence, message = self.validate(location)

            # Add validation metadata
            validated_location["confidence_score"] = confidence
            validated_location["validation_status"] = "verified" if is_valid else "needs_review"

            # Store validation details in metadata (optional)
            if self.config.get("store_validation_details", False):
                # Note: validation_details is not in the Location TypedDict
                # This would need to be added to the model if needed
                pass

            validated_locations.append(validated_location)

        return validated_locations
