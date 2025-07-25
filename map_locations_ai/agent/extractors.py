"""
Location extraction components for various input sources.

This module provides extractors that can identify and extract location information
from different types of input sources including text, URLs, and structured data.
"""

import os
import re
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from map_locations.common import Location, LocationList
from smolagents import ChatMessage, LiteLLMModel, ToolCallingAgent, tool

from ..utils.net_utils import classify_url, slug_to_name, url_title_fetch
from ..utils.nlp_utils import extract_entities


# Minimal extraction schema (before enrichment to full Location objects)
class ExtractedLocation:
    """Minimal extracted location data before enrichment."""

    def __init__(
        self,
        name: str,
        address_or_hint: str = "",
        source_type: str = "text",
        source_snippet_or_url: str = "",
        confidence: float = 0.5,
    ):
        self.name = name
        self.address_or_hint = address_or_hint
        self.source_type = source_type  # "text" or "url"
        self.source_snippet_or_url = source_snippet_or_url
        self.confidence = confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "name": self.name,
            "address_or_hint": self.address_or_hint,
            "source_type": self.source_type,
            "source_snippet_or_url": self.source_snippet_or_url,
            "confidence": self.confidence,
        }


class BaseExtractor(ABC):
    """Base class for all location extractors."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extractor with configuration.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

    @abstractmethod
    def extract(
        self, input_data: Union[str, List[str], Dict[str, Any]], **kwargs: Any
    ) -> List[ExtractedLocation]:
        """
        Extract locations from input data.

        Args:
            input_data: Input data to extract locations from (str, List[str], or Dict)
            **kwargs: Additional arguments

        Returns:
            List of extracted ExtractedLocation objects
        """
        pass


class TextExtractor(BaseExtractor):
    """Extract locations from text using pure LLM techniques."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize with LLM agent for extraction."""
        super().__init__(config)

        # Initialize LLM agent
        api_key = os.environ.get("LAVI_OPENAI_KEY")
        if not api_key:
            raise ValueError("LAVI_OPENAI_KEY environment variable is required")

        # Create LiteLLM model (gpt-4o)
        self.model = LiteLLMModel(model_id="gpt-4o", api_key=api_key)

        # Store system prompt for use in conversations
        self.system_prompt = """
You are an extraction-only agent. Your task is to list every location explicitly
named or linked in the user's input.

Rules:
1. Do NOT invent locations unless the text explicitly asks for suggestions.
2. For each item output:
   • name, address_or_hint, source_type, source_snippet_or_url, confidence
3. Preserve duplicates; de-duplication happens later.
4. Extract from complete addresses, venue names, attraction names, meeting points, etc.
5. Use confidence scores: 0.9 for explicit addresses, 0.7 for clear venue names,
   0.5 for ambiguous mentions
6. Output JSON array ONLY, no extra commentary.

Expected JSON format:
[
  {
    "name": "Location Name",
    "address_or_hint": "Address or hint text",
    "source_type": "text",
    "source_snippet_or_url": "exact text from input",
    "confidence": 0.8
  }
]
"""

    def extract(  # type: ignore[override]
        self, text: str, region: Optional[str] = None
    ) -> List[ExtractedLocation]:
        """
        Extract location mentions from text.

        Args:
            text: Input text to analyze
            region: Optional region hint for better resolution

        Returns:
            List of extracted ExtractedLocation objects
        """
        try:
            # Prepare prompt with region hint if provided
            user_prompt = f"Extract all locations from this text:\n\n{text}"
            if region:
                user_prompt += f"\n\nRegion hint: {region}"

            # Create messages for the LLM
            messages = [
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ]

            # Get LLM response using the model directly
            # LiteLLMModel uses __call__ method for completion
            response = self.model(messages)

            # Parse JSON response
            import json

            response_text = response.strip() if isinstance(response, str) else str(response)

            # Debug: print the response to see what we're getting
            print(f"DEBUG: Raw LLM response: {response_text[:200]}...")

            # Handle smol-agents ChatMessage response format
            if hasattr(response, "content"):
                response_text = response.content
            elif hasattr(response, "message"):
                response_text = response.message.content
            else:
                response_text = str(response)

            # Try to extract JSON from response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                try:
                    locations_data = json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"DEBUG: JSON parsing failed: {e}")
                    print(f"DEBUG: Attempted to parse: {json_str}")
                    return []
            else:
                # Try parsing the entire response as JSON
                try:
                    locations_data = json.loads(response_text)
                except json.JSONDecodeError as e:
                    print(f"DEBUG: Full response JSON parsing failed: {e}")
                    print(f"DEBUG: Full response: {response_text}")
                    return []

            # Convert to ExtractedLocation objects
            extracted_locations = []
            for loc_data in locations_data:
                if isinstance(loc_data, dict):
                    extracted_locations.append(
                        ExtractedLocation(
                            name=loc_data.get("name", "Unknown"),
                            address_or_hint=loc_data.get("address_or_hint", ""),
                            source_type="text",
                            source_snippet_or_url=loc_data.get("source_snippet_or_url", ""),
                            confidence=float(loc_data.get("confidence", 0.5)),
                        )
                    )

            return extracted_locations

        except Exception as e:
            print(f"Error in TextExtractor: {e}")
            import traceback

            traceback.print_exc()
            return []


class URLExtractor(BaseExtractor):
    """Extract locations from web URLs and their content."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize URL extractor."""
        super().__init__(config)
        self.timeout = self.config.get("timeout", 3)  # 3 second timeout as per plan

    def extract(  # type: ignore[override]
        self, urls: List[str], region: Optional[str] = None
    ) -> List[ExtractedLocation]:
        """
        Extract locations from web content.

        Args:
            urls: List of URLs to process
            region: Optional region hint

        Returns:
            List of extracted ExtractedLocation objects
        """
        extracted_locations = []

        for url in urls:
            try:
                # Use the improved net_utils functions
                title_result = url_title_fetch(url)
                slug_result = slug_to_name(url)
                url_classification = classify_url(url)

                # Determine best name and confidence
                name = "Unknown Website"
                confidence = 0.2

                if title_result.get("success") and title_result.get("title"):
                    name = title_result["title"]
                    confidence = 0.6
                elif slug_result.get("name"):
                    name = slug_result["name"]
                    confidence = slug_result.get("confidence", 0.3)

                # Adjust confidence based on URL classification
                url_conf = url_classification.get("confidence", 0.4)
                confidence = min(confidence, url_conf)

                # Add error context if available
                error_info = ""
                if title_result.get("error"):
                    error_info = f"Title fetch: {title_result['error']}"

                extracted_locations.append(
                    ExtractedLocation(
                        name=name,
                        address_or_hint=error_info,
                        source_type="url",
                        source_snippet_or_url=url,
                        confidence=confidence,
                    )
                )

            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                # Still create a low-confidence entry with fallback name
                try:
                    parsed = urlparse(url)
                    fallback_name = parsed.netloc or "Unknown Website"
                    if fallback_name.startswith("www."):
                        fallback_name = fallback_name[4:]
                except Exception:
                    fallback_name = "Unknown Website"

                extracted_locations.append(
                    ExtractedLocation(
                        name=fallback_name,
                        address_or_hint=f"Error: {str(e)}",
                        source_type="url",
                        source_snippet_or_url=url,
                        confidence=0.1,
                    )
                )

        return extracted_locations


class StructuredExtractor(BaseExtractor):
    """Extract locations from structured data formats."""

    def extract(  # type: ignore[override]
        self, data: Dict[str, Any], format_type: str = "auto"
    ) -> List[ExtractedLocation]:
        """
        Extract locations from structured data.

        Args:
            data: Structured data dictionary
            format_type: Data format type (json, csv, xml, auto)

        Returns:
            List of extracted ExtractedLocation objects
        """
        # Placeholder implementation for future structured data support
        # TODO: Implement structured data extraction
        return []
