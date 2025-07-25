"""
Tool functions for the LLM agent.

This module wraps deterministic functions with @tool decorators so they can be
used by the smol-agents ToolCallingAgent for location extraction.
"""

from typing import Any, Dict, List

from smolagents import tool

from .net_utils import classify_url, slug_to_name, url_title_fetch
from .nlp_utils import extract_entities, invitation_check, regex_addresses


@tool
def extract_entities_tool(text: str) -> List[Dict[str, Any]]:
    """
    Extract named entities using spaCy NER.

    Args:
        text: Text to analyze

    Returns:
        List of entity dictionaries with 'text', 'label', 'start', 'end'
    """
    return extract_entities(text)


@tool
def regex_addresses_tool(text: str) -> List[Dict[str, Any]]:
    """
    Extract addresses using regex patterns.

    Args:
        text: Text to analyze

    Returns:
        List of address dictionaries with 'text', 'confidence', 'pattern'
    """
    return regex_addresses(text)


@tool
def invitation_check_tool(text: str) -> Dict[str, Any]:
    """
    Detect if text invites extra location suggestions.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'invites_suggestions' boolean and 'confidence'
    """
    return invitation_check(text)


@tool
def url_title_fetch_tool(url: str) -> Dict[str, Any]:
    """
    Fast title fetch from URL (≤3 s timeout).

    Args:
        url: URL to fetch title from

    Returns:
        Dictionary with 'title', 'success', 'error' fields
    """
    return url_title_fetch(url)


@tool
def slug_to_name_tool(url: str) -> Dict[str, Any]:
    """
    Derive name from URL slug.

    Args:
        url: URL to extract name from

    Returns:
        Dictionary with 'name', 'confidence' fields
    """
    return slug_to_name(url)


@tool
def classify_url_tool(url: str) -> Dict[str, Any]:
    """
    Classify URL type for confidence scoring.

    Args:
        url: URL to classify

    Returns:
        Dictionary with 'type', 'confidence' fields
    """
    return classify_url(url)
