"""
Enhanced extraction agent using ToolCallingAgent with deterministic tools.

This module implements the agent-based extraction approach as specified in the
extractors plan, using smol-agents ToolCallingAgent with @tool-decorated functions.
"""

import os
from typing import Any, Dict, List, Optional

from smolagents import ChatMessage, LiteLLMModel, ToolCallingAgent

from ..utils.tools import (
    classify_url_tool,
    extract_entities_tool,
    invitation_check_tool,
    regex_addresses_tool,
    slug_to_name_tool,
    url_title_fetch_tool,
)
from .extractors import ExtractedLocation


class ExtractionAgent:
    """
    Enhanced extraction agent using ToolCallingAgent with deterministic tools.

    This agent combines LLM reasoning with deterministic tool functions for
    high-recall, high-precision location extraction.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the extraction agent.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}

        # Get API key
        api_key = os.environ.get("LAVI_OPENAI_KEY")
        if not api_key:
            raise ValueError("LAVI_OPENAI_KEY environment variable is required")

        # Create LiteLLM model (gpt-4o as default)
        model_id = self.config.get("model_id", "gpt-4o")
        self.model = LiteLLMModel(model_id=model_id, api_key=api_key)

        # Create ToolCallingAgent with available tools
        self.agent = ToolCallingAgent(
            model=self.model,
            tools=[
                extract_entities_tool,
                regex_addresses_tool,
                invitation_check_tool,
                url_title_fetch_tool,
                slug_to_name_tool,
                classify_url_tool,
            ],
        )

        # System prompt for extraction agent
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
6. When a tool can accomplish the task more accurately or efficiently, use it.
7. Output JSON array ONLY, no extra commentary.

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

Available tools:
- extract_entities_tool: Extract named entities using spaCy NER
- regex_addresses_tool: Extract addresses using regex patterns
- invitation_check_tool: Detect if text invites extra suggestions
- url_title_fetch_tool: Fast title fetch from URLs
- slug_to_name_tool: Derive name from URL slug
- classify_url_tool: Classify URL type for confidence scoring
"""

    def extract_locations(self, text: str, region: Optional[str] = None) -> List[ExtractedLocation]:
        """
        Extract locations from text using the enhanced agent.

        Args:
            text: Input text to analyze
            region: Optional region hint for better resolution

        Returns:
            List of extracted ExtractedLocation objects
        """
        try:
            # Prepare user prompt
            user_prompt = f"Extract all locations from this text:\n\n{text}"
            if region:
                user_prompt += f"\n\nRegion hint: {region}"

            # Create messages
            messages = [
                ChatMessage(role="system", content=self.system_prompt),
                ChatMessage(role="user", content=user_prompt),
            ]

            # Get response from agent
            response = self.agent.run(messages)

            # Parse JSON response
            import json

            response_text = response.strip() if isinstance(response, str) else str(response)

            # Try to extract JSON from response
            json_start = response_text.find("[")
            json_end = response_text.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                locations_data = json.loads(json_str)
            else:
                # Try parsing the entire response as JSON
                locations_data = json.loads(response_text)

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
            print(f"Error in ExtractionAgent: {e}")
            import traceback

            traceback.print_exc()
            return []

    def extract_from_urls(
        self, urls: List[str], region: Optional[str] = None
    ) -> List[ExtractedLocation]:
        """
        Extract locations from URLs using the enhanced agent.

        Args:
            urls: List of URLs to process
            region: Optional region hint

        Returns:
            List of extracted ExtractedLocation objects
        """
        extracted_locations = []

        for url in urls:
            try:
                # Use tools to process URL
                url_classification = classify_url_tool(url)
                title_result = url_title_fetch_tool(url)
                slug_result = slug_to_name_tool(url)

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

                extracted_locations.append(
                    ExtractedLocation(
                        name=name,
                        address_or_hint="",
                        source_type="url",
                        source_snippet_or_url=url,
                        confidence=confidence,
                    )
                )

            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                # Create low-confidence entry
                extracted_locations.append(
                    ExtractedLocation(
                        name="Unknown Website",
                        address_or_hint="",
                        source_type="url",
                        source_snippet_or_url=url,
                        confidence=0.1,
                    )
                )

        return extracted_locations
