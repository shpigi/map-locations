"""
YAML processing component for the Map Locations AI pipeline.

Handles YAML parsing, validation, error recovery, and partial data extraction.
"""

from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI

from .models import LLMResult


class YAMLProcessor:
    """Handles YAML parsing, validation, and error recovery."""

    def __init__(
        self,
        client: Optional[OpenAI] = None,
        llm_config: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the YAML processor.

        Args:
            client: OpenAI client for error recovery (None for testing)
            llm_config: LLM configuration for error recovery
        """
        self.client = client
        self.llm_config = llm_config or {"model": "gpt-4o-mini", "timeout": 120}

    def parse_yaml_response(self, raw_response: str) -> List[Dict[str, Any]]:
        """
        Parse YAML response from LLM.

        Args:
            raw_response: Raw response text from LLM

        Returns:
            List of parsed location dictionaries

        Raises:
            ValueError: If response format is invalid
        """
        # Clean the response - extract YAML if wrapped in markdown
        cleaned_response = self._clean_response_format(raw_response)

        parsed_data = yaml.safe_load(cleaned_response)
        if not isinstance(parsed_data, dict) or "locations" not in parsed_data:
            raise ValueError("Response does not contain 'locations' key")

        parsed_locations = parsed_data["locations"]
        if not isinstance(parsed_locations, list):
            raise ValueError("Locations is not a list")

        # Validate each location has required fields
        self._validate_locations(parsed_locations)

        return parsed_locations

    def _clean_response_format(self, response: str) -> str:
        """
        Clean response format by removing markdown wrapping.

        Args:
            response: Raw response string

        Returns:
            Cleaned YAML string
        """
        cleaned_response = response.strip()
        if cleaned_response.startswith("```yaml"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        return cleaned_response.strip()

    def _validate_locations(self, locations: List[Dict[str, Any]]) -> None:
        """
        Validate that all locations have required fields.

        Args:
            locations: List of location dictionaries

        Raises:
            ValueError: If any location is missing required fields
        """
        required_fields = [
            "name",
            "type",
            "description",
            "source_text",
            "confidence",
            "is_url",
        ]

        for i, loc in enumerate(locations):
            for field in required_fields:
                if field not in loc:
                    print(f"Location {i} missing required field: {field}")
                    print(f"Location data: {loc}")
                    print("-" * 30)
                    raise ValueError(f"Location {i} missing required field: {field}")

    def fix_malformed_yaml(
        self, raw_response: str, chunk_id: str, original_processing_time: float
    ) -> LLMResult:
        """
        Attempt to fix malformed YAML using LLM.

        Args:
            raw_response: The malformed YAML response
            chunk_id: ID of the chunk being processed
            original_processing_time: Processing time from original call

        Returns:
            LLMResult with fixed response or failure
        """
        fix_prompt = self._create_fix_prompt(raw_response)

        try:
            # Check if we have a client (for testing environments)
            if self.client is None:
                raise ValueError("No OpenAI client available for YAML fixing")

            import time

            fix_start_time = time.time()

            # Use max_completion_tokens for o4 models, max_tokens for others
            model = self.llm_config["model"]
            if model.startswith("o4"):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": fix_prompt}],
                    temperature=0.1,  # Lower temperature for fixing
                    max_completion_tokens=2000,
                    timeout=self.llm_config["timeout"],
                    calling_module="YAMLProcessor",
                    operation_type="yaml_fix",
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": fix_prompt}],
                    temperature=0.1,  # Lower temperature for fixing
                    max_tokens=2000,
                    timeout=self.llm_config["timeout"],
                    calling_module="YAMLProcessor",
                    operation_type="yaml_fix",
                )

            fix_processing_time = time.time() - fix_start_time
            total_processing_time_ms = original_processing_time + (
                fix_processing_time * 1000
            )

            fixed_response = response.choices[0].message.content
            if fixed_response is None:
                raise ValueError("Empty response from LLM")

            fixed_response = fixed_response.strip()
            cleaned_fixed_response = self._clean_response_format(fixed_response)

            # Try to parse the fixed YAML
            try:
                parsed_locations = self.parse_yaml_response(cleaned_fixed_response)

                return LLMResult(
                    success=True,
                    raw_response=cleaned_fixed_response,
                    parsed_locations=parsed_locations,
                    processing_time=(
                        original_processing_time + fix_processing_time * 1000
                    )
                    / 1000,
                    processing_time_ms=total_processing_time_ms,
                    error=None,
                )

            except (yaml.YAMLError, ValueError) as e:
                print(f"Fixed YAML still invalid: {e}")
                print(f"Fixed response: {cleaned_fixed_response}")

                # Try partial extraction as last resort
                partial_locations = self.extract_partial_locations(
                    cleaned_fixed_response
                )
                if partial_locations:
                    return LLMResult(
                        success=True,
                        raw_response=cleaned_fixed_response,
                        parsed_locations=partial_locations,
                        processing_time=(
                            original_processing_time + fix_processing_time * 1000
                        )
                        / 1000,
                        processing_time_ms=total_processing_time_ms,
                        error=f"Partial extraction after YAML fix: {e}",
                    )

                return LLMResult(
                    success=False,
                    raw_response=cleaned_fixed_response,
                    parsed_locations=[],
                    processing_time=(
                        original_processing_time + fix_processing_time * 1000
                    )
                    / 1000,
                    processing_time_ms=total_processing_time_ms,
                    error=f"YAML fixing failed: {e}",
                )

        except Exception as e:
            return LLMResult(
                success=False,
                raw_response=raw_response,
                parsed_locations=[],
                processing_time=original_processing_time / 1000,
                processing_time_ms=original_processing_time,
                error=f"Failed to fix YAML: {e}",
            )

    def _create_fix_prompt(self, raw_response: str) -> str:
        """Create prompt for fixing malformed YAML."""
        return f"""The following YAML response is malformed and cannot be parsed.
Please fix the YAML format without losing any information. Return ONLY valid YAML.

Malformed YAML:
{raw_response}

Requirements:
1. Fix any indentation issues
2. Ensure all strings are properly quoted and escaped
3. Maintain all location information
4. Return valid YAML with 'locations:' key
5. Each location must have: name, type, description, source_text, confidence, is_url, url
6. Use proper YAML syntax with consistent indentation
7. Quote all string values to avoid parsing issues

Example of correct format:
locations:
  - name: "Location Name"
    type: "landmark"
    description: "Brief description"
    source_text: "Exact text from input"
    confidence: 0.8
    is_url: false
    url: ""

Fixed YAML:"""

    def extract_partial_locations(self, yaml_text: str) -> List[Dict[str, Any]]:
        """
        Extract locations from partially malformed YAML using text parsing.

        Args:
            yaml_text: Malformed YAML text

        Returns:
            List of partially extracted location dictionaries
        """
        locations = []
        lines = yaml_text.split("\n")
        current_location: Dict[str, Any] = {}
        in_location = False

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check if this is a location entry start
            if (
                line.startswith("- name:")
                or line.startswith("-name:")
                or line.startswith("- name :")
            ):
                if (
                    current_location and len(current_location) >= 4
                ):  # At least name, type, description, source_text
                    locations.append(current_location)
                current_location = {}
                in_location = True
                # Extract name
                name_match = line.split(":", 1)
                if len(name_match) > 1:
                    current_location["name"] = name_match[1].strip().strip("\"'")
                    current_location["type"] = "unknown"
                    current_location["description"] = "Extracted from partial data"
                    current_location["source_text"] = "Partial extraction"
                    current_location["confidence"] = 0.3
                    current_location["is_url"] = False
                    current_location["url"] = ""
            elif in_location and ":" in line:
                parts = line.split(":", 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip().strip("\"'")

                    if key in [
                        "name",
                        "type",
                        "description",
                        "source_text",
                        "confidence",
                        "is_url",
                        "url",
                    ]:
                        if key == "confidence":
                            try:
                                current_location[key] = float(value)
                            except ValueError:
                                current_location[key] = 0.5
                        elif key == "is_url":
                            current_location[key] = value.lower() in [
                                "true",
                                "1",
                                "yes",
                            ]
                        else:
                            current_location[key] = value

        # Add the last location if it exists
        if current_location and len(current_location) >= 4:
            locations.append(current_location)

        return locations

    def fix_individual_location(
        self, location_data: Dict[str, Any], chunk_id: str
    ) -> Dict[str, Any]:
        """
        Fix individual location format issues.

        Args:
            location_data: Malformed location data
            chunk_id: ID of the chunk being processed

        Returns:
            Fixed location dictionary

        Raises:
            ValueError: If location cannot be fixed
        """
        fix_prompt = f"""
The following location data is malformed.
Please fix the format while preserving all information.

Malformed location:
{location_data}

Requirements:
1. Ensure all required fields are present:
    name, type, description, source_text, confidence, is_url, url
2. Fix any formatting issues
3. Return valid YAML for a single location

Fixed location:"""

        try:
            # Check if we have a client (for testing environments)
            if self.client is None:
                raise ValueError("No OpenAI client available for location fixing")

            # Use max_completion_tokens for o4 models, max_tokens for others
            model = self.llm_config["model"]
            if model.startswith("o4"):
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a YAML formatting expert. Fix malformed location data "
                                "while preserving all information."
                            ),
                        },
                        {"role": "user", "content": fix_prompt},
                    ],
                    max_completion_tokens=500,
                    timeout=self.llm_config["timeout"],
                    calling_module="YAMLProcessor",
                    operation_type="location_fix",
                )
            else:
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a YAML formatting expert. Fix malformed location data "
                                "while preserving all information."
                            ),
                        },
                        {"role": "user", "content": fix_prompt},
                    ],
                    temperature=0.1,
                    max_tokens=500,
                    timeout=self.llm_config["timeout"],
                    calling_module="YAMLProcessor",
                    operation_type="location_fix",
                )

            fixed_response = response.choices[0].message.content
            if fixed_response is None:
                raise ValueError("Empty response from LLM")
            fixed_response = fixed_response.strip()
            cleaned_response = self._clean_response_format(fixed_response)

            # Try to parse the fixed location
            try:
                parsed_location = yaml.safe_load(cleaned_response)
                if not isinstance(parsed_location, dict):
                    raise ValueError("Fixed response is not a dictionary")

                # Validate required fields
                required_fields = [
                    "name",
                    "type",
                    "description",
                    "source_text",
                    "confidence",
                    "is_url",
                ]
                for field in required_fields:
                    if field not in parsed_location:
                        parsed_location[field] = self._get_default_field_value(field)

                return parsed_location

            except yaml.YAMLError as e:
                raise ValueError(f"Fixed location is still invalid YAML: {e}")

        except Exception as e:
            raise ValueError(f"Failed to fix location: {e}")

    def _get_default_field_value(self, field: str) -> Any:
        """Get default value for missing fields."""
        defaults = {
            "name": "Unknown Location",
            "type": "unknown",
            "description": "No description available",
            "source_text": "Missing source text",
            "confidence": 0.3,
            "is_url": False,
            "url": "",
        }
        return defaults.get(field, "")
