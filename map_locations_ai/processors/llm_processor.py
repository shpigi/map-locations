"""
LLM processing component for the Map Locations AI pipeline.

Handles OpenAI LLM communication, response parsing, and error recovery.
"""

import time
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import yaml
from openai import OpenAI

from .models import ChunkData, LLMResult


class LLMProcessor:
    """Manages LLM communication and error handling."""

    def __init__(
        self,
        client: Optional[OpenAI],
        agent_prompt: str,
        model: str = "gpt-4o-mini",
        temperature: float = 0.1,
        max_tokens: int = 2000,
        timeout: int = 120,
    ):
        """
        Initialize the LLM processor.

        Args:
            client: OpenAI client instance (None for testing)
            agent_prompt: System prompt for the AI agent
            model: OpenAI model to use
            temperature: Temperature setting for generation
            max_tokens: Maximum tokens in response
            timeout: Request timeout in seconds
        """
        self.client = client
        self.agent_prompt = agent_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout

    def call_llm(self, chunk_data: ChunkData, retry_count: int = 0) -> LLMResult:
        """
        Make LLM call for location extraction with retry logic.

        Args:
            chunk_data: Text chunk to process
            retry_count: Number of retries attempted

        Returns:
            LLMResult with processing outcome
        """
        start_time = time.time()

        # Check if we have a client (for testing environments)
        if self.client is None:
            return self._create_mock_response()

        # Prepare the prompt
        user_message = self._format_extraction_prompt(chunk_data.text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.agent_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )

            processing_time = time.time() - start_time
            processing_time_ms = processing_time * 1000

            # Extract response content
            raw_response = response.choices[0].message.content
            if raw_response is None:
                raise ValueError("Empty response from LLM")

            raw_response = raw_response.strip()

            # Try to parse the response
            try:
                parsed_locations = self._parse_yaml_response(raw_response)

                return LLMResult(
                    success=True,
                    raw_response=raw_response,
                    parsed_locations=parsed_locations,
                    processing_time=processing_time,
                    processing_time_ms=processing_time_ms,
                    error=None,
                )

            except (yaml.YAMLError, ValueError) as e:
                # Print debug information
                print(f"YAML parsing failed for chunk {chunk_data.id}:")
                print(f"Error: {e}")
                print(f"Raw response: {raw_response}")
                print("-" * 50)

                # Retry once if YAML parsing fails
                if retry_count < 1:
                    print(f"YAML parsing failed, retrying chunk {chunk_data.id}...")
                    return self.call_llm(chunk_data, retry_count + 1)
                else:
                    # Try to fix the YAML using LLM
                    print(f"YAML parsing failed after retry, attempting to fix...")
                    return self._fix_yaml_response(
                        raw_response, chunk_data, processing_time_ms
                    )

        except Exception as e:
            processing_time = time.time() - start_time
            processing_time_ms = processing_time * 1000

            return LLMResult(
                success=False,
                raw_response="",
                parsed_locations=[],
                processing_time=processing_time,
                processing_time_ms=processing_time_ms,
                error=str(e),
            )

    def _format_extraction_prompt(self, text: str) -> str:
        """
        Format the extraction prompt for the LLM.

        Args:
            text: Text chunk to process

        Returns:
            Formatted prompt string
        """
        return f"""Please extract all locations from the following text chunk:

{text}

IMPORTANT: Return ONLY valid YAML format with proper indentation.
Each location must have all required fields.
Ensure proper YAML structure and indentation. Do not include any markdown formatting.

 Example format:
 locations:
   - name: "Location Name"
     type: "landmark"
     description: "Brief description"
     source_text: "Exact text from input"
     confidence: 0.8
     is_url: false
     url: ""
     """

    def _parse_yaml_response(self, raw_response: str) -> list:
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
        cleaned_response = raw_response.strip()
        if cleaned_response.startswith("```yaml"):
            cleaned_response = cleaned_response[7:]
        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()

        parsed_data = yaml.safe_load(cleaned_response)
        if not isinstance(parsed_data, dict) or "locations" not in parsed_data:
            raise ValueError("Response does not contain 'locations' key")

        parsed_locations = parsed_data["locations"]
        if not isinstance(parsed_locations, list):
            raise ValueError("Locations is not a list")

        # Validate each location has required fields
        required_fields = [
            "name",
            "type",
            "description",
            "source_text",
            "confidence",
            "is_url",
        ]

        for i, loc in enumerate(parsed_locations):
            for field in required_fields:
                if field not in loc:
                    print(f"Location {i} missing required field: {field}")
                    print(f"Location data: {loc}")
                    print("-" * 30)
                    raise ValueError(f"Location {i} missing required field: {field}")

        return parsed_locations

    def _fix_yaml_response(
        self, raw_response: str, chunk_data: ChunkData, original_processing_time: float
    ) -> LLMResult:
        """
        Attempt to fix malformed YAML using LLM.

        Args:
            raw_response: The malformed YAML response
            chunk_data: Original chunk data
            original_processing_time: Processing time from original call

        Returns:
            LLMResult with fixed response or failure
        """
        fix_prompt = f"""The following YAML response is malformed and cannot be parsed.
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

        try:
            # Check if we have a client (for testing environments)
            if self.client is None:
                return self._create_mock_fixed_response()

            fix_start_time = time.time()

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": fix_prompt}],
                temperature=0.1,  # Lower temperature for fixing
                max_tokens=self.max_tokens,
                timeout=self.timeout,
            )

            fix_processing_time = time.time() - fix_start_time
            total_processing_time_ms = original_processing_time + (
                fix_processing_time * 1000
            )

            fixed_response = response.choices[0].message.content
            if fixed_response is None:
                raise ValueError("Empty response from LLM")

            fixed_response = fixed_response.strip()

            # Clean the fixed response
            if fixed_response.startswith("```yaml"):
                fixed_response = fixed_response[7:]
            elif fixed_response.startswith("```"):
                fixed_response = fixed_response[3:]
            if fixed_response.endswith("```"):
                fixed_response = fixed_response[:-3]
            fixed_response = fixed_response.strip()

            # Try to parse the fixed YAML
            try:
                parsed_locations = self._parse_yaml_response(fixed_response)

                return LLMResult(
                    success=True,
                    raw_response=fixed_response,
                    parsed_locations=parsed_locations,
                    processing_time=(original_processing_time + fix_processing_time)
                    / 1000,
                    processing_time_ms=total_processing_time_ms,
                    error=None,
                )

            except (yaml.YAMLError, ValueError) as e:
                print(f"Fixed YAML still invalid: {e}")
                print(f"Fixed response: {fixed_response}")

                return LLMResult(
                    success=False,
                    raw_response=fixed_response,
                    parsed_locations=[],
                    processing_time=(original_processing_time + fix_processing_time)
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

    def _create_mock_response(self) -> LLMResult:
        """Create mock response for testing."""
        return LLMResult(
            success=True,
            raw_response=(
                'locations:\n  - name: "Test Location"\n    type: "landmark"\n'
                '    description: "Mock location for testing"\n    source_text: "Test text"\n'
                '    confidence: 0.8\n    is_url: false\n    url: ""'
            ),
            parsed_locations=[
                {
                    "name": "Test Location",
                    "type": "landmark",
                    "description": "Mock location for testing",
                    "source_text": "Test text",
                    "confidence": 0.8,
                    "is_url": False,
                    "url": "",
                }
            ],
            processing_time=0.0,
            processing_time_ms=0.0,
            error=None,
        )

    def _create_mock_fixed_response(self) -> LLMResult:
        """Create mock fixed response for testing."""
        return LLMResult(
            success=True,
            raw_response=(
                'locations:\n  - name: "Fixed Test Location"\n    type: "landmark"\n'
                '    description: "Mock fixed location for testing"\n'
                '    source_text: "Test text"\n'
                '    confidence: 0.8\n    is_url: false\n    url: ""'
            ),
            parsed_locations=[
                {
                    "name": "Fixed Test Location",
                    "type": "landmark",
                    "description": "Mock fixed location for testing",
                    "source_text": "Test text",
                    "confidence": 0.8,
                    "is_url": False,
                    "url": "",
                }
            ],
            processing_time=0.0,
            processing_time_ms=0.0,
            error=None,
        )
