#!/usr/bin/env python3
"""
Map Locations AI - Simplified Pipeline
Processes text files to extract location information using OpenAI LLM.
"""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI


class LocationExtractionPipeline:
    """Main pipeline for location extraction from text files."""

    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the pipeline with configuration."""
        self.config = self._load_config(config_path)
        self.locations_memory: List[Dict[str, Any]] = []
        self.trace_data: List[Dict[str, Any]] = []

        # Set up OpenAI client
        api_key = os.getenv("LAVI_OPENAI_KEY")
        if not api_key:
            raise ValueError("LAVI_OPENAI_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)

        # Load agent prompt
        self.agent_prompt = self._load_agent_prompt()

        # Create directories
        self._setup_directories()

    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config: Any = yaml.safe_load(f)
                if config is None:
                    raise ValueError("Empty configuration file")
                if not isinstance(config, dict):
                    raise ValueError("Configuration must be a dictionary")
                return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")

    def _load_agent_prompt(self) -> str:
        """Load the agent prompt from file."""
        prompt_path = Path("agent_prompt.txt")
        if not prompt_path.exists():
            raise FileNotFoundError("agent_prompt.txt not found")

        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read().strip()

    def _setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        temp_dir = Path(self.config["output"]["temp_dir"])
        trace_dir = Path(self.config["output"]["trace_dir"])

        temp_dir.mkdir(exist_ok=True)
        trace_dir.mkdir(exist_ok=True)

    def _read_file_chunks(self, file_path: str) -> List[Dict[str, Any]]:
        """Read file and split into overlapping chunks."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                lines = f.readlines()

        chunk_size = self.config["processing"]["chunk_size"]
        overlap_size = self.config["processing"]["overlap_size"]

        chunks: List[Dict[str, Any]] = []
        total_lines = len(lines)

        if total_lines == 0:
            return chunks

        start = 0
        chunk_id = 1

        while start < total_lines:
            # Calculate end position
            end = min(start + chunk_size, total_lines)

            # Extract chunk text
            chunk_lines = lines[start:end]
            chunk_text = "".join(chunk_lines)

            chunks.append(
                {
                    "id": f"chunk_{chunk_id:03d}",
                    "text": chunk_text,
                    "start_line": start + 1,  # 1-indexed
                    "end_line": end,
                    "total_lines": len(chunk_lines),
                }
            )

            # Move start position (with overlap)
            if end >= total_lines:
                break

            start = end - overlap_size
            chunk_id += 1

        return chunks

    def _call_llm(self, chunk_data: Dict[str, Any], retry_count: int = 0) -> Dict[str, Any]:
        """Make LLM call for location extraction with retry logic."""
        start_time = time.time()

        # Prepare the prompt with emphasis on valid YAML
        user_message = (
            f"""Please extract all locations from the following text chunk:

{chunk_data['text']}

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
    url: """
            ""
        )

        try:
            response = self.client.chat.completions.create(
                model=self.config["llm"]["model"],
                messages=[
                    {"role": "system", "content": self.agent_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=self.config["llm"]["temperature"],
                max_tokens=self.config["llm"]["max_tokens"],
                timeout=self.config["llm"]["timeout"],
            )

            processing_time = (time.time() - start_time) * 1000  # Convert to ms

            # Extract response content
            raw_response = response.choices[0].message.content
            if raw_response is None:
                raise ValueError("Empty response from LLM")
            raw_response = raw_response.strip()

            # Try to parse YAML with cleaning
            try:
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
                for i, loc in enumerate(parsed_locations):
                    required_fields = [
                        "name",
                        "type",
                        "description",
                        "source_text",
                        "confidence",
                        "is_url",
                    ]
                    for field in required_fields:
                        if field not in loc:
                            print(f"Location {i} missing required field: {field}")
                            print(f"Location data: {loc}")
                            print("-" * 30)
                            raise ValueError(f"Location {i} missing required field: {field}")

            except (yaml.YAMLError, ValueError) as e:
                # Print the problematic YAML for debugging
                print(f"YAML parsing failed for chunk {chunk_data['id']}:")
                print(f"Error: {e}")
                print(f"Raw response: {raw_response}")
                print(f"Cleaned response: {cleaned_response}")
                print("-" * 50)

                # Retry once if YAML parsing fails
                if retry_count < 1:
                    print(f"YAML parsing failed, retrying chunk {chunk_data['id']}...")
                    return self._call_llm(chunk_data, retry_count + 1)
                else:
                    # Try to fix the YAML using LLM
                    print(f"YAML parsing failed after retry, attempting to fix...")
                    return self._fix_yaml_response(raw_response, chunk_data, processing_time)

            return {
                "success": True,
                "raw_response": raw_response,
                "parsed_locations": parsed_locations,
                "processing_time_ms": processing_time,
                "error": None,
            }

        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "raw_response": None,
                "parsed_locations": [],
                "processing_time_ms": processing_time,
                "error": str(e),
            }

    def _fix_yaml_response(
        self, raw_response: str, chunk_data: Dict[str, Any], processing_time: float
    ) -> Dict[str, Any]:
        """Attempt to fix malformed YAML using LLM."""
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

        # Trace the fixing attempt
        fix_trace_entry: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": f"{chunk_data['id']}_fix_attempt",
            "input": {
                "fix_prompt": fix_prompt,
                "original_raw_response": raw_response,
                "model": self.config["llm"]["model"],
                "temperature": 0.1,
            },
            "output": {
                "success": False,
                "raw_response": None,
                "parsed_locations": [],
                "processing_time_ms": 0,
            },
            "errors": [],
        }

        try:
            response = self.client.chat.completions.create(
                model=self.config["llm"]["model"],
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a YAML formatting expert. Fix malformed YAML while "
                            "preserving all information. Return ONLY valid YAML."
                        ),
                    },
                    {"role": "user", "content": fix_prompt},
                ],
                temperature=0.1,
                max_tokens=self.config["llm"]["max_tokens"],
                timeout=self.config["llm"]["timeout"],
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
                parsed_data = yaml.safe_load(fixed_response)
                if not isinstance(parsed_data, dict) or "locations" not in parsed_data:
                    raise ValueError("Fixed response does not contain 'locations' key")

                parsed_locations = parsed_data["locations"]
                if not isinstance(parsed_locations, list):
                    raise ValueError("Fixed locations is not a list")

                # Validate each location has required fields
                for i, loc in enumerate(parsed_locations):
                    required_fields = [
                        "name",
                        "type",
                        "description",
                        "source_text",
                        "confidence",
                        "is_url",
                    ]
                    for field in required_fields:
                        if field not in loc:
                            print(f"Fixed location {i} missing required field: {field}")
                            print(f"Fixed location data: {loc}")
                            print("-" * 30)
                            raise ValueError(f"Fixed location {i} missing required field: {field}")

                # Update trace with success
                fix_trace_entry["output"].update(
                    {
                        "success": True,
                        "raw_response": fixed_response,
                        "parsed_locations": parsed_locations,
                        "processing_time_ms": processing_time,
                    }
                )
                self._write_trace_entry(fix_trace_entry)

                return {
                    "success": True,
                    "raw_response": fixed_response,
                    "parsed_locations": parsed_locations,
                    "processing_time_ms": processing_time,
                    "error": None,
                }

            except (yaml.YAMLError, ValueError) as e:
                # Try to extract any valid locations from the malformed YAML
                print(f"YAML fixing failed, attempting to extract partial data...")
                print(f"Fixed response that still failed: {fixed_response}")
                print(f"Error: {e}")
                print("-" * 50)

                try:
                    partial_locations = self._extract_partial_locations(fixed_response)
                    if partial_locations:
                        # Update trace with partial success
                        fix_trace_entry["output"].update(
                            {
                                "success": True,
                                "raw_response": fixed_response,
                                "parsed_locations": partial_locations,
                                "processing_time_ms": processing_time,
                            }
                        )
                        fix_trace_entry["errors"] = [f"Partial extraction: {e}"]
                        self._write_trace_entry(fix_trace_entry)

                        return {
                            "success": True,
                            "raw_response": fixed_response,
                            "parsed_locations": partial_locations,
                            "processing_time_ms": processing_time,
                            "error": f"Partial extraction: {e}",
                        }
                except Exception:
                    pass

                return {
                    "success": False,
                    "raw_response": fixed_response,
                    "parsed_locations": [],
                    "processing_time_ms": processing_time,
                    "error": f"Failed to fix YAML: {e}",
                }

        except Exception as e:
            return {
                "success": False,
                "raw_response": raw_response,
                "parsed_locations": [],
                "processing_time_ms": processing_time,
                "error": f"Failed to fix YAML: {e}",
            }

    def _fix_individual_location(
        self, location_data: Dict[str, Any], chunk_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Fix individual location format issues."""
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
            response = self.client.chat.completions.create(
                model=self.config["llm"]["model"],
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
                timeout=self.config["llm"]["timeout"],
            )

            fixed_response = response.choices[0].message.content.strip()

            # Clean the fixed response
            if fixed_response.startswith("```yaml"):
                fixed_response = fixed_response[7:]
            elif fixed_response.startswith("```"):
                fixed_response = fixed_response[3:]
            if fixed_response.endswith("```"):
                fixed_response = fixed_response[:-3]
            fixed_response = fixed_response.strip()

            # Try to parse the fixed location
            try:
                parsed_location = yaml.safe_load(fixed_response)
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
                        raise ValueError(f"Fixed location missing required field: {field}")

                return parsed_location

            except (yaml.YAMLError, ValueError) as e:
                raise ValueError(f"Failed to fix location: {e}")

        except Exception as e:
            raise ValueError(f"Failed to fix location: {e}")

    def _extract_partial_locations(self, yaml_text: str) -> List[Dict[str, Any]]:
        """Extract locations from partially malformed YAML."""
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
                            current_location[key] = value.lower() in ["true", "1", "yes"]
                        else:
                            current_location[key] = value

        # Add the last location if it exists
        if current_location and len(current_location) >= 4:
            locations.append(current_location)

        return locations

    def _write_trace_entry(self, trace_entry: Dict[str, Any]) -> None:
        """Write a single trace entry to file immediately."""
        trace_dir = Path(self.config["output"]["trace_dir"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{timestamp}.json"
        filepath = trace_dir / filename

        # Create a simple trace entry with just this call
        trace_log = {
            "run_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "single_entry": True,
                "chunk_id": trace_entry["chunk_id"],
            },
            "trace": trace_entry,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_log, f, indent=2, ensure_ascii=False)

        print(f"Trace written to: {filepath}")

    def _trace_llm_call(self, chunk_data: Dict[str, Any], llm_result: Dict[str, Any]) -> None:
        """Add LLM call to trace data and write to file immediately."""
        trace_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "chunk_id": chunk_data["id"],
            "input": {
                "chunk_text": (
                    chunk_data["text"][:500] + "..."
                    if len(chunk_data["text"]) > 500
                    else chunk_data["text"]
                ),
                "start_line": chunk_data["start_line"],
                "end_line": chunk_data["end_line"],
                "model": self.config["llm"]["model"],
                "temperature": self.config["llm"]["temperature"],
            },
            "output": {
                "success": llm_result["success"],
                "raw_response": llm_result["raw_response"],
                "parsed_locations": llm_result["parsed_locations"],
                "processing_time_ms": llm_result["processing_time_ms"],
            },
            "errors": [llm_result["error"]] if llm_result["error"] else [],
        }

        self.trace_data.append(trace_entry)

        # Write trace to file immediately
        self._write_trace_entry(trace_entry)

    def _save_chunk_yaml(self, chunk_data: Dict[str, Any], locations: List[Dict[str, Any]]) -> str:
        """Save locations from a chunk to individual YAML file."""
        chunk_prefix = self.config["output"]["chunk_prefix"]
        temp_dir = Path(self.config["output"]["temp_dir"])

        filename = f"{chunk_prefix}_{chunk_data['id']}.yaml"
        filepath = temp_dir / filename

        # Prepare YAML data
        yaml_data = {
            "chunk_info": {
                "id": chunk_data["id"],
                "start_line": chunk_data["start_line"],
                "end_line": chunk_data["end_line"],
                "total_lines": chunk_data["total_lines"],
            },
            "locations": locations,
        }

        # Save to YAML file
        with open(filepath, "w", encoding="utf-8") as f:
            yaml.dump(yaml_data, f, default_flow_style=False, allow_unicode=True, indent=2)

        return str(filepath)

    def _save_trace_log(self, input_file: str) -> str:
        """Save trace data to JSON file."""
        trace_dir = Path(self.config["output"]["trace_dir"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"run_{timestamp}.json"
        filepath = trace_dir / filename

        trace_log = {
            "run_info": {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "input_file": input_file,
                "total_chunks": len(
                    [t for t in self.trace_data if t["chunk_id"].startswith("chunk_")]
                ),
                "total_locations": len(self.locations_memory),
                "config": self.config,
            },
            "traces": self.trace_data,
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(trace_log, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def process_file(self, input_file: str) -> Dict[str, Any]:
        """Process a single file and extract locations."""
        print(f"Processing file: {input_file}")

        # Reset state
        self.locations_memory.clear()
        self.trace_data.clear()

        # Read file into chunks
        try:
            chunks = self._read_file_chunks(input_file)
            print(f"Split into {len(chunks)} chunks")
        except Exception as e:
            raise RuntimeError(f"Failed to read file: {e}")

        # Process each chunk
        chunk_files = []
        for i, chunk_data in enumerate(chunks, 1):
            print(f"Processing chunk {i}/{len(chunks)}: {chunk_data['id']}")

            # Call LLM
            llm_result = self._call_llm(chunk_data)

            # Trace the call
            self._trace_llm_call(chunk_data, llm_result)

            # Check for errors
            if not llm_result["success"]:
                print(f"LLM call failed for {chunk_data['id']}: {llm_result['error']}")
                # Don't raise immediately, let the pipeline continue to see all errors
                # The trace will show the problematic output

            # Add to memory
            locations = llm_result["parsed_locations"]
            self.locations_memory.extend(locations)

            # Save chunk YAML
            chunk_file = self._save_chunk_yaml(chunk_data, locations)
            chunk_files.append(chunk_file)

            print(f"  Extracted {len(locations)} locations")

        # Save trace log
        trace_file = self._save_trace_log(input_file)

        # Return summary
        return {
            "input_file": input_file,
            "total_chunks": len(chunks),
            "total_locations": len(self.locations_memory),
            "chunk_files": chunk_files,
            "trace_file": trace_file,
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Extract locations from text files")
    parser.add_argument("input_file", help="Path to input text file")
    parser.add_argument("--config", default="config.yaml", help="Path to configuration file")

    args = parser.parse_args()

    # Validate input file
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        return 1

    try:
        # Initialize pipeline
        pipeline = LocationExtractionPipeline(args.config)

        # Process file
        result = pipeline.process_file(args.input_file)

        # Print summary
        print("\n" + "=" * 50)
        print("PROCESSING COMPLETE")
        print("=" * 50)
        print(f"Input file: {result['input_file']}")
        print(f"Total chunks: {result['total_chunks']}")
        print(f"Total locations: {result['total_locations']}")
        print(f"Chunk files: {len(result['chunk_files'])}")
        print(f"Trace file: {result['trace_file']}")
        print("\nChunk files created:")
        for chunk_file in result["chunk_files"]:
            print(f"  {chunk_file}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
