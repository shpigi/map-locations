"""
Shared data models for map-locations packages.

This module defines the core Location data structure used across
all map-locations packages.
"""

from typing import List, TypedDict


class Location(TypedDict, total=False):
    """Type definition for a location entry.

    Core Fields (required):
        name: The name of the location
        type: The type/category of the location
        latitude: Latitude coordinate
        longitude: Longitude coordinate

    Standard Fields (optional):
        address: Address of the location
        tags: List of tags for filtering
        neighborhood: Neighborhood or area name
        date_added: Date when location was added (YYYY-MM-DD format)
        date_of_visit: Date when location was visited (YYYY-MM-DD format)

    AI-Enhanced Fields (optional, added by AI agent):
        description: Tourist-friendly description of the location
        official_website: Official website URL
        booking_url: URL for booking/tickets
        reviews_url: URL to reviews (TripAdvisor, Google, etc.)
        opening_hours: Operating hours information
        price_range: Price range indicator (e.g., "$", "$$", "$$$")
        duration_recommended: Recommended visit duration
        best_time_to_visit: Best time of day/season to visit
        accessibility_info: Accessibility information
        nearby_attractions: List of nearby points of interest

    Metadata Fields (optional, for tracking data quality):
        data_sources: List of sources used to gather information
        confidence_score: Confidence score for the location data (0.0-1.0)
        last_updated: ISO timestamp when data was last updated
        validation_status: Validation status (verified, pending, needs_review)
    """

    # Core required fields
    name: str
    type: str
    latitude: float
    longitude: float

    # Standard optional fields
    address: str
    tags: List[str]
    neighborhood: str
    date_added: str
    date_of_visit: str

    # AI-enhanced fields
    description: str
    official_website: str
    booking_url: str
    reviews_url: str
    opening_hours: str
    price_range: str
    duration_recommended: str
    best_time_to_visit: str
    accessibility_info: str
    nearby_attractions: List[str]

    # Metadata fields
    data_sources: List[str]
    confidence_score: float
    last_updated: str
    validation_status: str


# Type aliases for common collections
LocationList = List[Location]
