"""
NLP utility functions for location extraction.

This module provides deterministic NLP functions that can be wrapped as tools
for the LLM agent to use during location extraction.
"""

import re
from typing import Any, Dict, List, Optional

try:
    import spacy

    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False


def extract_entities(text: str) -> List[Dict[str, Any]]:
    """
    Extract named entities using spaCy NER.

    Args:
        text: Text to analyze

    Returns:
        List of entity dictionaries with 'text', 'label', 'start', 'end'
    """
    if not SPACY_AVAILABLE:
        return []

    try:
        # Load spaCy model (en_core_web_sm as specified in plan)
        nlp = spacy.load("en_core_web_sm")
        doc = nlp(text)

        entities = []
        for ent in doc.ents:
            # Focus on location-related entities as per plan
            if ent.label_ in {"GPE", "LOC", "FAC"}:
                entities.append(
                    {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                        "description": spacy.explain(ent.label_),
                    }
                )

        return entities
    except Exception as e:
        print(f"Error in spaCy NER: {e}")
        return []


def regex_addresses(text: str) -> List[Dict[str, Any]]:
    """
    Extract addresses using regex patterns.

    Args:
        text: Text to analyze

    Returns:
        List of address dictionaries with 'text', 'confidence', 'pattern'
    """
    addresses = []

    # Pattern 1: Street address with postal code
    # Matches: "145 Rue du Temple, 75003 Paris"
    pattern1 = r"\d+\s+[^,]+?,\s*\d{4,5}\s+[^,\n]+"
    matches1 = re.finditer(pattern1, text, re.IGNORECASE)

    for match in matches1:
        addresses.append(
            {"text": match.group(), "confidence": 0.9, "pattern": "street_with_postal"}
        )

    # Pattern 2: Simple address with city
    # Matches: "Eiffel Tower, Paris"
    pattern2 = r"[A-Z][^,]+?,\s*[A-Z][^,\n]+"
    matches2 = re.finditer(pattern2, text)

    for match in matches2:
        addresses.append({"text": match.group(), "confidence": 0.7, "pattern": "venue_with_city"})

    # Pattern 3: Key phrases that indicate locations
    # Matches: "meet us at", "Stay at", etc.
    key_phrases = [
        r"meet us at\s+([^.\n]+)",
        r"Please meet us at\s+([^.\n]+)",
        r"Stay at\s+([^.\n]+)",
        r"Staying at\s+([^.\n]+)",
        r"meeting point[:\s]+([^.\n]+)",
        r"meeting spot[:\s]+([^.\n]+)",
    ]

    for i, pattern in enumerate(key_phrases):
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            addresses.append(
                {"text": match.group(1).strip(), "confidence": 0.8, "pattern": f"key_phrase_{i}"}
            )

    return addresses


def invitation_check(text: str) -> Dict[str, Any]:
    """
    Detect if text invites extra location suggestions.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with 'invites_suggestions' boolean and 'confidence'
    """
    invitation_phrases = [
        r"additional\s+(?:best\s+)?(?:museums?|restaurants?|attractions?)",
        r"more\s+(?:options?|suggestions?)",
        r"other\s+(?:places?|sites?)",
        r"also\s+(?:visit|see|check)",
        r"you\s+might\s+also\s+like",
        r"consider\s+also",
        r"alternatives?",
        r"other\s+recommendations?",
    ]

    text_lower = text.lower()
    matches = []

    for phrase in invitation_phrases:
        if re.search(phrase, text_lower):
            matches.append(phrase)

    invites_suggestions = len(matches) > 0
    confidence = min(0.9, 0.3 + len(matches) * 0.2)

    return {
        "invites_suggestions": invites_suggestions,
        "confidence": confidence,
        "matched_phrases": matches,
    }
