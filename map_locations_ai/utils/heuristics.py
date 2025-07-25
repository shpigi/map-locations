"""
Heuristic text analysis functions for location extraction.

This module provides deterministic heuristic functions that can be wrapped as tools
for the LLM agent to use during location extraction.
"""

import re
from typing import Any, Dict, List, Optional


def detect_meeting_points(text: str) -> Dict[str, Any]:
    """
    Detect meeting points in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'meeting_points' list and 'confidence'
    """
    meeting_phrases = [
        r"meet\s+(?:us\s+)?at\s+([^.\n]+)",
        r"meeting\s+point[:\s]+([^.\n]+)",
        r"meeting\s+spot[:\s]+([^.\n]+)",
        r"meet\s+(?:up\s+)?(?:at|in)\s+([^.\n]+)",
        r"gather\s+(?:at|in)\s+([^.\n]+)",
        r"meet\s+(?:you\s+)?(?:at|in)\s+([^.\n]+)",
        r"pick\s+(?:you\s+)?up\s+(?:at|in)\s+([^.\n]+)",
        r"wait\s+(?:for\s+you\s+)?(?:at|in)\s+([^.\n]+)",
    ]

    meeting_points = []
    text_lower = text.lower()

    for phrase in meeting_phrases:
        matches = re.finditer(phrase, text_lower)
        for match in matches:
            location = match.group(1).strip()
            if location and len(location) > 2:  # Avoid very short matches
                meeting_points.append({"location": location, "pattern": phrase, "confidence": 0.8})

    return {
        "meeting_points": meeting_points,
        "confidence": min(0.9, 0.3 + len(meeting_points) * 0.2),
    }


def detect_accommodations(text: str) -> Dict[str, Any]:
    """
    Detect accommodation mentions in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'accommodations' list and 'confidence'
    """
    accommodation_phrases = [
        r"stay\s+(?:at|in)\s+([^.\n]+)",
        r"staying\s+(?:at|in)\s+([^.\n]+)",
        r"hotel[:\s]+([^.\n]+)",
        r"hostel[:\s]+([^.\n]+)",
        r"airbnb[:\s]+([^.\n]+)",
        r"guesthouse[:\s]+([^.\n]+)",
        r"bed\s+and\s+breakfast[:\s]+([^.\n]+)",
        r"resort[:\s]+([^.\n]+)",
        r"lodge[:\s]+([^.\n]+)",
        r"inn[:\s]+([^.\n]+)",
        r"booked\s+(?:at|in)\s+([^.\n]+)",
        r"reservation\s+(?:at|in)\s+([^.\n]+)",
        r"check\s+in\s+(?:at|in)\s+([^.\n]+)",
        r"check\s+out\s+(?:at|in)\s+([^.\n]+)",
    ]

    accommodations = []
    text_lower = text.lower()

    for phrase in accommodation_phrases:
        matches = re.finditer(phrase, text_lower)
        for match in matches:
            location = match.group(1).strip()
            if location and len(location) > 2:
                accommodations.append({"location": location, "pattern": phrase, "confidence": 0.9})

    return {
        "accommodations": accommodations,
        "confidence": min(0.9, 0.3 + len(accommodations) * 0.2),
    }


def detect_attractions(text: str) -> Dict[str, Any]:
    """
    Detect tourist attractions in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'attractions' list and 'confidence'
    """
    attraction_phrases = [
        r"visit\s+([^.\n]+)",
        r"see\s+([^.\n]+)",
        r"check\s+out\s+([^.\n]+)",
        r"explore\s+([^.\n]+)",
        r"tour\s+([^.\n]+)",
        r"guided\s+tour\s+(?:of\s+)?([^.\n]+)",
        r"museum[:\s]+([^.\n]+)",
        r"gallery[:\s]+([^.\n]+)",
        r"exhibition[:\s]+([^.\n]+)",
        r"monument[:\s]+([^.\n]+)",
        r"landmark[:\s]+([^.\n]+)",
        r"statue[:\s]+([^.\n]+)",
        r"palace[:\s]+([^.\n]+)",
        r"castle[:\s]+([^.\n]+)",
        r"cathedral[:\s]+([^.\n]+)",
        r"church[:\s]+([^.\n]+)",
        r"temple[:\s]+([^.\n]+)",
        r"mosque[:\s]+([^.\n]+)",
        r"synagogue[:\s]+([^.\n]+)",
        r"park[:\s]+([^.\n]+)",
        r"garden[:\s]+([^.\n]+)",
        r"plaza[:\s]+([^.\n]+)",
        r"square[:\s]+([^.\n]+)",
        r"bridge[:\s]+([^.\n]+)",
        r"tower[:\s]+([^.\n]+)",
        r"fountain[:\s]+([^.\n]+)",
        r"arch[:\s]+([^.\n]+)",
        r"gate[:\s]+([^.\n]+)",
        r"wall[:\s]+([^.\n]+)",
    ]

    attractions = []
    text_lower = text.lower()

    for phrase in attraction_phrases:
        matches = re.finditer(phrase, text_lower)
        for match in matches:
            location = match.group(1).strip()
            if location and len(location) > 2:
                attractions.append({"location": location, "pattern": phrase, "confidence": 0.8})

    return {"attractions": attractions, "confidence": min(0.9, 0.3 + len(attractions) * 0.1)}


def detect_time_mentions(text: str) -> Dict[str, Any]:
    """
    Detect time mentions for scheduled activities.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'time_mentions' list and 'confidence'
    """
    time_phrases = [
        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s+(?:at|in)\s+([^.\n]+)",
        r"at\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s+(?:at|in)\s+([^.\n]+)",
        r"meet\s+(?:at|in)\s+([^.\n]+)\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s+(?:meet|meeting)\s+(?:at|in)\s+([^.\n]+)",
        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s+(?:visit|see)\s+([^.\n]+)",
        r"visit\s+([^.\n]+)\s+at\s+(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\s+(?:lunch|dinner|breakfast)\s+(?:at|in)\s+([^.\n]+)",
        r"(lunch|dinner|breakfast)\s+(?:at|in)\s+([^.\n]+)\s+at\s+"
        r"(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)",
    ]

    time_mentions = []
    text_lower = text.lower()

    for phrase in time_phrases:
        matches = re.finditer(phrase, text_lower)
        for match in matches:
            if len(match.groups()) >= 2:
                time_str = match.group(1).strip()
                location = match.group(2).strip()
                if location and len(location) > 2:
                    time_mentions.append(
                        {
                            "time": time_str,
                            "location": location,
                            "pattern": phrase,
                            "confidence": 0.7,
                        }
                    )

    return {"time_mentions": time_mentions, "confidence": min(0.9, 0.3 + len(time_mentions) * 0.2)}


def detect_booking_references(text: str) -> Dict[str, Any]:
    """
    Detect booking references in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'booking_references' list and 'confidence'
    """
    booking_phrases = [
        r"booked\s+(?:at|in)\s+([^.\n]+)",
        r"reservation\s+(?:at|in)\s+([^.\n]+)",
        r"booking\s+(?:at|in)\s+([^.\n]+)",
        r"reserved\s+(?:at|in)\s+([^.\n]+)",
        r"confirmed\s+(?:at|in)\s+([^.\n]+)",
        r"paid\s+(?:for\s+)?(?:at|in)\s+([^.\n]+)",
        r"purchased\s+(?:at|in)\s+([^.\n]+)",
        r"bought\s+(?:tickets?\s+)?(?:for|to)\s+([^.\n]+)",
        r"ordered\s+(?:at|in)\s+([^.\n]+)",
        r"scheduled\s+(?:at|in)\s+([^.\n]+)",
        r"appointment\s+(?:at|in)\s+([^.\n]+)",
        r"session\s+(?:at|in)\s+([^.\n]+)",
        r"class\s+(?:at|in)\s+([^.\n]+)",
        r"workshop\s+(?:at|in)\s+([^.\n]+)",
        r"event\s+(?:at|in)\s+([^.\n]+)",
        r"concert\s+(?:at|in)\s+([^.\n]+)",
        r"show\s+(?:at|in)\s+([^.\n]+)",
        r"performance\s+(?:at|in)\s+([^.\n]+)",
        r"tour\s+(?:at|in)\s+([^.\n]+)",
        r"guided\s+tour\s+(?:at|in)\s+([^.\n]+)",
    ]

    booking_references = []
    text_lower = text.lower()

    for phrase in booking_phrases:
        matches = re.finditer(phrase, text_lower)
        for match in matches:
            location = match.group(1).strip()
            if location and len(location) > 2:
                booking_references.append(
                    {"location": location, "pattern": phrase, "confidence": 0.9}
                )

    return {
        "booking_references": booking_references,
        "confidence": min(0.9, 0.3 + len(booking_references) * 0.2),
    }
