"""
Network utility functions for URL processing.

This module provides deterministic network functions that can be wrapped as tools
for the LLM agent to use during URL-based location extraction.
"""

import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def url_title_fetch(url: str) -> Dict[str, Any]:
    """
    Fast title fetch from URL (≤3 s timeout as per plan).

    Args:
        url: URL to fetch title from

    Returns:
        Dictionary with 'title', 'success', 'error' fields
    """
    try:
        # Fast title fetch with 3-second timeout as specified
        response = requests.get(url, timeout=3)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Try multiple title sources as per plan
        title = None

        # Try Open Graph title
        og_title = soup.find("meta", property="og:title")
        if og_title and og_title.get("content"):
            title = og_title["content"]

        # Try Twitter title
        if not title:
            twitter_title = soup.find("meta", name="twitter:title")
            if twitter_title and twitter_title.get("content"):
                title = twitter_title["content"]

        # Try regular title tag
        if not title:
            title_tag = soup.find("title")
            if title_tag:
                title = title_tag.get_text().strip()

        if title:
            return {"title": title, "success": True, "error": None, "source": "html_title"}
        else:
            return {"title": None, "success": False, "error": "No title found", "source": None}

    except Exception as e:
        return {"title": None, "success": False, "error": str(e), "source": None}


def slug_to_name(url: str) -> Dict[str, Any]:
    """
    Derive name from URL slug.

    Args:
        url: URL to extract name from

    Returns:
        Dictionary with 'name', 'confidence' fields
    """
    try:
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split("/") if p]

        if not path_parts:
            # Use domain name as fallback
            domain = parsed.netloc
            if domain.startswith("www."):
                domain = domain[4:]
            name = domain.replace(".", " ").title()
            confidence = 0.3
        else:
            # Use last path segment
            slug = path_parts[-1]
            # Clean up the slug
            name = slug.replace("-", " ").replace("_", " ").title()
            # Remove common file extensions
            name = re.sub(r"\.(html?|php|asp|jsp)$", "", name, flags=re.IGNORECASE)
            confidence = 0.5

        return {"name": name, "confidence": confidence, "source": "url_slug"}

    except Exception as e:
        return {"name": "Unknown Website", "confidence": 0.1, "source": "error", "error": str(e)}


def classify_url(url: str) -> Dict[str, Any]:
    """
    Classify URL type for confidence scoring.

    Args:
        url: URL to classify

    Returns:
        Dictionary with 'type', 'confidence' fields
    """
    url_lower = url.lower()

    # Gmail threads get low confidence as per plan
    if "mail.google.com" in url_lower:
        return {
            "type": "gmail_thread",
            "confidence": 0.2,
            "reason": "Gmail threads typically have low location relevance",
        }

    # Travel/tourism sites get higher confidence
    travel_domains = [
        "tripadvisor",
        "booking.com",
        "airbnb",
        "expedia",
        "lonelyplanet",
        "roughguides",
        "fodors",
        "ricksteves",
        "visit",
        "tourism",
        "travel",
    ]

    for domain in travel_domains:
        if domain in url_lower:
            return {"type": "travel_site", "confidence": 0.7, "reason": f"Travel site: {domain}"}

    # Museum/cultural sites
    cultural_domains = [
        "museum",
        "gallery",
        "exhibition",
        "art",
        "culture",
        "heritage",
        "historic",
        "monument",
    ]

    for domain in cultural_domains:
        if domain in url_lower:
            return {
                "type": "cultural_site",
                "confidence": 0.8,
                "reason": f"Cultural site: {domain}",
            }

    # Default classification
    return {"type": "general", "confidence": 0.4, "reason": "General website"}
