"""
Configuration management component for the Map Locations AI pipeline.

Handles configuration loading, validation, and access to different configuration sections.
"""

from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class ConfigManager:
    """Centralized configuration management."""

    def __init__(
        self, config_path: str = "config.yaml", input_filename: Optional[str] = None
    ):
        """
        Initialize the configuration manager.

        Args:
            config_path: Path to the configuration file
            input_filename: Input filename to use in output paths (optional)
        """
        self.config_path = config_path
        self.config = self.load_config(config_path)
        self.agent_prompt = self._load_agent_prompt()
        self.input_filename = input_filename

    def load_config(self, config_path: str) -> Dict[str, Any]:
        """
        Load configuration from YAML file.

        Args:
            config_path: Path to the configuration file

        Returns:
            Dictionary with configuration data

        Raises:
            FileNotFoundError: If configuration file not found
            ValueError: If configuration is invalid
        """
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config: Any = yaml.safe_load(f)
                if config is None:
                    raise ValueError("Empty configuration file")
                if not isinstance(config, dict):
                    raise ValueError("Configuration must be a dictionary")

                # Validate configuration structure
                self._validate_config(config)
                return config

        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML configuration: {e}")

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate configuration structure.

        Args:
            config: Configuration dictionary to validate

        Raises:
            ValueError: If required configuration sections are missing
        """
        required_sections = ["llm", "processing", "output"]
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Missing required configuration section: {section}")

        # Validate LLM section
        llm_config = config["llm"]
        required_llm_fields = ["model", "temperature", "max_tokens", "timeout"]
        for field in required_llm_fields:
            if field not in llm_config:
                raise ValueError(f"Missing required LLM configuration field: {field}")

        # Validate processing section
        processing_config = config["processing"]
        required_processing_fields = ["chunk_size", "overlap_size"]
        for field in required_processing_fields:
            if field not in processing_config:
                raise ValueError(
                    f"Missing required processing configuration field: {field}"
                )

        # Validate output section
        output_config = config["output"]
        required_output_fields = ["temp_dir", "trace_dir", "chunk_prefix"]
        for field in required_output_fields:
            if field not in output_config:
                raise ValueError(
                    f"Missing required output configuration field: {field}"
                )

    def _load_agent_prompt(self) -> str:
        """
        Load the agent prompt from file.

        Returns:
            Agent prompt string

        Raises:
            FileNotFoundError: If prompt file not found
        """
        # Try multiple possible paths for the agent prompt
        possible_paths = [
            Path("agent_prompt.txt"),  # Same directory
            Path("map_locations_ai/agent_prompt.txt"),  # From project root
            Path("../agent_prompt.txt"),  # Parent directory
        ]

        for prompt_path in possible_paths:
            if prompt_path.exists():
                with open(prompt_path, "r", encoding="utf-8") as f:
                    return f.read().strip()

        raise FileNotFoundError("agent_prompt.txt not found in any expected location")

    def get_llm_config(self) -> Dict[str, Any]:
        """
        Get LLM configuration section.

        Returns:
            Dictionary with LLM configuration
        """
        return dict(self.config["llm"])

    def get_model_for_step(self, step: str) -> str:
        """
        Get the appropriate model for a specific processing step.

        Args:
            step: Processing step (extraction, enrichment, geocoding, deduplication)

        Returns:
            Model name for the step
        """
        models = self.config["llm"].get("models", {})
        return str(models.get(step, self.config["llm"].get("model", "gpt-4o-mini")))

    def get_processing_config(self) -> Dict[str, Any]:
        """
        Get processing configuration section.

        Returns:
            Dictionary with processing configuration
        """
        return dict(self.config["processing"])

    def get_output_config(self) -> Dict[str, Any]:
        """
        Get output configuration section.

        Returns:
            Dictionary with output configuration
        """
        return dict(self.config["output"])

    def get_deduplication_config(self) -> Dict[str, Any]:
        """
        Get deduplication configuration section.

        Returns:
            Dictionary with deduplication configuration, or defaults if not present
        """
        return dict(
            self.config.get(
                "deduplication",
                {
                    "similarity_threshold": 0.75,
                    "name_weight": 0.4,
                    "type_weight": 0.2,
                    "description_weight": 0.25,
                    "source_weight": 0.15,
                    "merge_strategy": {
                        "name": "highest_confidence",
                        "type": "most_specific",
                        "description": "longest",
                        "confidence": "weighted_average",
                        "source_text": "concatenate",
                    },
                },
            )
        )

    def get_enrichment_config(self) -> Dict[str, Any]:
        """
        Get enrichment configuration section.

        Returns:
            Dictionary with enrichment configuration, or defaults if not present
        """
        return dict(
            self.config.get(
                "enrichment",
                {
                    "enabled": True,
                    "model": "gpt-4o-mini",
                    "max_searches_per_location": 3,
                    "temperature": 0.1,
                    "timeout": 120,
                    "priority_fields": [
                        "latitude",
                        "longitude",
                        "name",
                        "description",
                        "official_website",
                        "opening_hours",
                    ],
                    "batch_size": 10,
                    "rate_limit_delay": 1.0,
                },
            )
        )

    def get_full_config(self) -> Dict[str, Any]:
        """
        Get complete configuration.

        Returns:
            Dictionary with full configuration
        """
        return dict(self.config)

    def get_agent_prompt(self) -> str:
        """
        Get the agent prompt.

        Returns:
            Agent prompt string
        """
        return self.agent_prompt

    def update_config_section(self, section: str, updates: Dict[str, Any]) -> None:
        """
        Update a configuration section.

        Args:
            section: Name of the configuration section
            updates: Dictionary of updates to apply
        """
        if section not in self.config:
            self.config[section] = {}

        self.config[section].update(updates)

    def save_config(self, output_path: Optional[str] = None) -> None:
        """
        Save current configuration to file.

        Args:
            output_path: Path to save config (defaults to original path)
        """
        save_path = output_path or self.config_path

        with open(save_path, "w", encoding="utf-8") as f:
            yaml.dump(self.config, f, default_flow_style=False, indent=2)

    def get_temp_dir(self) -> Path:
        """
        Get temporary directory path.

        Returns:
            Path object for temp directory
        """
        base_temp_dir = Path(self.config["output"]["temp_dir"])

        if self.input_filename:
            # Extract filename without extension
            input_name = Path(self.input_filename).stem
            return base_temp_dir / input_name
        else:
            return base_temp_dir

    def get_trace_dir(self) -> Path:
        """
        Get trace directory path.

        Returns:
            Path object for trace directory
        """
        base_trace_dir = Path(self.config["output"]["trace_dir"])

        if self.input_filename:
            # Extract filename without extension
            input_name = Path(self.input_filename).stem
            return base_trace_dir / input_name
        else:
            return base_trace_dir

    def get_chunk_prefix(self) -> str:
        """
        Get chunk file prefix.

        Returns:
            Chunk file prefix string
        """
        return str(self.config["output"]["chunk_prefix"])

    def setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        temp_dir = self.get_temp_dir()
        trace_dir = self.get_trace_dir()

        temp_dir.mkdir(exist_ok=True)
        trace_dir.mkdir(exist_ok=True)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.

        Returns:
            Dictionary with configuration summary
        """
        return {
            "config_file": self.config_path,
            "llm_model": self.config["llm"]["model"],
            "chunk_size": self.config["processing"]["chunk_size"],
            "overlap_size": self.config["processing"]["overlap_size"],
            "temp_dir": str(self.get_temp_dir()),
            "trace_dir": str(self.get_trace_dir()),
            "chunk_prefix": self.get_chunk_prefix(),
            "has_deduplication_config": "deduplication" in self.config,
            "sections": list(self.config.keys()),
        }
