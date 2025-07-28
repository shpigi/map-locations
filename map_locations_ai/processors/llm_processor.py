"""
LLM processing component for the Map Locations AI pipeline.

Handles OpenAI LLM communication, response parsing, and error recovery.
"""

import csv
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI

from .models import ChunkData, LLMResult


class LLMUsageTracker:
    """Tracks LLM usage and logs to CSV file."""

    _instance = None
    _initialized = False

    def __new__(cls, output_dir: Optional[Path] = None):
        """Singleton pattern - ensure only one instance exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Initialize the LLM usage tracker.

        Args:
            output_dir: Directory to save the CSV file (only used on first initialization)
        """
        # Only initialize once
        if not self._initialized and output_dir is not None:
            self.output_dir = output_dir
            self.csv_path = output_dir / "llm_calls.csv"
            self._initialize_csv()
            self._initialized = True
        elif not self._initialized:
            # Default initialization if no output_dir provided
            from pathlib import Path

            self.output_dir = Path("map_locations_ai/temp")
            self.csv_path = self.output_dir / "llm_calls.csv"
            self._initialize_csv()
            self._initialized = True

    @classmethod
    def get_instance(cls) -> "LLMUsageTracker":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def initialize(cls, output_dir: Path) -> "LLMUsageTracker":
        """Initialize the singleton with a specific output directory."""
        instance = cls(output_dir)
        return instance

    def _initialize_csv(self) -> None:
        """Initialize the CSV file with headers if it doesn't exist."""
        if not self.csv_path.exists():
            self.output_dir.mkdir(parents=True, exist_ok=True)
            with open(self.csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "timestamp",
                        "calling_module",
                        "model",
                        "temperature",
                        "max_tokens",
                        "timeout",
                        "input_tokens",
                        "output_tokens",
                        "total_tokens",
                        "processing_time_ms",
                        "success",
                        "error_message",
                        "input_length",
                        "output_length",
                        "retry_count",
                        "operation_type",
                    ]
                )

    def log_llm_call(
        self,
        calling_module: str,
        model: str,
        temperature: float,
        max_tokens: int,
        timeout: int,
        input_tokens: Optional[int],
        output_tokens: Optional[int],
        total_tokens: Optional[int],
        processing_time_ms: float,
        success: bool,
        error_message: Optional[str],
        input_text: str,
        output_text: str,
        retry_count: int = 0,
        operation_type: str = "extraction",
    ) -> None:
        """
        Log an LLM call to the CSV file.

        Args:
            calling_module: Name of the module making the call
            model: LLM model used
            temperature: Temperature setting
            max_tokens: Maximum tokens setting
            timeout: Timeout setting
            input_tokens: Number of input tokens (if available)
            output_tokens: Number of output tokens (if available)
            total_tokens: Total tokens used (if available)
            processing_time_ms: Processing time in milliseconds
            success: Whether the call was successful
            error_message: Error message if failed
            input_text: Input text sent to LLM
            output_text: Output text received from LLM
            retry_count: Number of retries attempted
            operation_type: Type of operation (extraction, enrichment, etc.)
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        with open(self.csv_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    timestamp,
                    calling_module,
                    model,
                    temperature,
                    max_tokens,
                    timeout,
                    input_tokens if input_tokens is not None else "",
                    output_tokens if output_tokens is not None else "",
                    total_tokens if total_tokens is not None else "",
                    processing_time_ms,
                    success,
                    error_message or "",
                    len(input_text),
                    len(output_text),
                    retry_count,
                    operation_type,
                ]
            )


class TrackedChatCompletions:
    """Wrapper for OpenAI chat completions with usage tracking."""

    def __init__(self, client: "TrackedOpenAI", usage_tracker: LLMUsageTracker):
        self.client = client
        self.usage_tracker = usage_tracker
        self._original_chat = client._original_chat

    @property
    def completions(self):
        """Return tracked completions interface."""
        return TrackedCompletions(self.client, self.usage_tracker)


class TrackedCompletions:
    """Wrapper for OpenAI completions with usage tracking."""

    def __init__(self, client: "TrackedOpenAI", usage_tracker: LLMUsageTracker):
        self.client = client
        self.usage_tracker = usage_tracker
        self._original_completions = client._original_chat.completions

    def create(self, model: str, messages: List[Dict[str, str]], **kwargs):
        """
        Create a chat completion with usage tracking.

        Args:
            model: The model to use
            messages: The messages to send
            **kwargs: Additional arguments for the OpenAI API

        Returns:
            The OpenAI response

        Raises:
            Exception: If the API call fails
        """
        start_time = time.time()

        # Extract tracking parameters from kwargs
        calling_module = kwargs.pop("calling_module", "unknown")
        operation_type = kwargs.pop("operation_type", "unknown")
        retry_count = kwargs.pop("retry_count", 0)

        # Extract standard parameters
        temperature = kwargs.get("temperature", 0.1)
        max_tokens = kwargs.get("max_tokens", 2000)
        timeout = kwargs.get("timeout", 120)

        try:
            # Make the actual API call
            response = self._original_completions.create(
                model=model, messages=messages, **kwargs
            )

            # Extract token usage if available
            input_tokens = None
            output_tokens = None
            total_tokens = None
            if hasattr(response, "usage") and response.usage:
                input_tokens = getattr(response.usage, "prompt_tokens", None)
                output_tokens = getattr(response.usage, "completion_tokens", None)
                total_tokens = getattr(response.usage, "total_tokens", None)

            processing_time_ms = (time.time() - start_time) * 1000

            # Extract response content
            output_text = ""
            if response.choices and response.choices[0].message:
                output_text = response.choices[0].message.content or ""

            # Log successful call
            self.usage_tracker.log_llm_call(
                calling_module=calling_module,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                processing_time_ms=processing_time_ms,
                success=True,
                error_message=None,
                input_text=str(messages)[:1000],  # Truncate for logging
                output_text=output_text[:1000],  # Truncate for logging
                retry_count=retry_count,
                operation_type=operation_type,
            )

            return response

        except Exception as e:
            processing_time_ms = (time.time() - start_time) * 1000

            # Log failed call
            self.usage_tracker.log_llm_call(
                calling_module=calling_module,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
                input_tokens=None,
                output_tokens=None,
                total_tokens=None,
                processing_time_ms=processing_time_ms,
                success=False,
                error_message=str(e),
                input_text=str(messages)[:1000],  # Truncate for logging
                output_text="",
                retry_count=retry_count,
                operation_type=operation_type,
            )
            raise


class TrackedOpenAI(OpenAI):
    """OpenAI client with automatic usage tracking."""

    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the tracked OpenAI client.

        Args:
            api_key: OpenAI API key
            **kwargs: Additional arguments for OpenAI client
        """
        super().__init__(api_key=api_key, **kwargs)
        self.usage_tracker = LLMUsageTracker.get_instance()
        self._original_chat = super().chat  # Store original chat method

    @property
    def chat(self):
        """Return tracked chat completions wrapper."""
        return TrackedChatCompletions(self, self.usage_tracker)


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
        calling_module: str = "LLMProcessor",
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
            calling_module: Name of the calling module for tracking
        """
        self.client = client
        self.agent_prompt = agent_prompt
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.calling_module = calling_module

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
            # Use max_completion_tokens for o4 models, max_tokens for others
            if self.model.startswith("o4"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.agent_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    max_completion_tokens=self.max_tokens,
                    timeout=self.timeout,
                    calling_module=self.calling_module,
                    operation_type="extraction",
                    retry_count=retry_count,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.agent_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                    calling_module=self.calling_module,
                    operation_type="extraction",
                    retry_count=retry_count,
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

            # Use max_completion_tokens for o4 models, max_tokens for others
            if self.model.startswith("o4"):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": fix_prompt}],
                    max_completion_tokens=self.max_tokens,
                    timeout=self.timeout,
                    calling_module=self.calling_module,
                    operation_type="yaml_fix",
                    retry_count=1,
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": fix_prompt}],
                    temperature=0.1,  # Lower temperature for fixing
                    max_tokens=self.max_tokens,
                    timeout=self.timeout,
                    calling_module=self.calling_module,
                    operation_type="yaml_fix",
                    retry_count=1,
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
