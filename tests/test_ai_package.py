"""
Tests for the AI package functionality.
"""

from pathlib import Path

import pytest

from map_locations_ai.pipeline import LocationExtractionPipeline


class TestAIPackage:
    """Test AI package basic functionality."""

    def test_ai_package_import(self):
        """Test that the AI package can be imported."""
        from map_locations_ai.pipeline import LocationExtractionPipeline

        assert LocationExtractionPipeline is not None

    def test_pipeline_initialization(self):
        """Test that the LocationExtractionPipeline can be initialized."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        assert pipeline is not None
        assert hasattr(pipeline, "config")

    def test_pipeline_with_config(self):
        """Test pipeline initialization with configuration."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        assert pipeline is not None
        assert hasattr(pipeline, "config")

    def test_pipeline_methods_exist(self):
        """Test that pipeline methods exist."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        assert hasattr(pipeline, "process_file")
        assert hasattr(pipeline, "_call_llm")
        assert hasattr(pipeline, "_read_file_chunks")

    def test_pipeline_config_structure(self):
        """Test that pipeline config has expected structure."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        assert "llm" in pipeline.config
        assert "processing" in pipeline.config
        assert "output" in pipeline.config

    def test_pipeline_directories_creation(self):
        """Test that pipeline creates necessary directories."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        temp_dir = Path(pipeline.config["output"]["temp_dir"])
        trace_dir = Path(pipeline.config["output"]["trace_dir"])

        # Directories should be created during initialization
        assert temp_dir.exists()
        assert trace_dir.exists()

    def test_chunk_processing(self):
        """Test that file chunking works correctly."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")

        # Create a test file
        test_file = Path("test_input.txt")
        test_content = "Line 1\nLine 2\nLine 3\n" * 20  # 60 lines
        test_file.write_text(test_content)

        try:
            chunks = pipeline._read_file_chunks(str(test_file))
            assert len(chunks) > 0
            assert all("id" in chunk for chunk in chunks)
            assert all("text" in chunk for chunk in chunks)
        finally:
            test_file.unlink(missing_ok=True)

    def test_agent_prompt_loading(self):
        """Test that agent prompt can be loaded."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        prompt = pipeline._load_agent_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 0


class TestAIPackageCLI:
    """Test AI package CLI functionality."""

    def test_cli_script_exists(self):
        """Test that CLI script exists."""
        pipeline_script = Path("map_locations_ai/pipeline.py")
        assert pipeline_script.exists()

    def test_cli_main_function_exists(self):
        """Test that main function exists in pipeline."""
        from map_locations_ai.pipeline import main

        assert main is not None
        assert callable(main)


class TestAIPackageConfiguration:
    """Test AI package configuration."""

    def test_config_file_exists(self):
        """Test that config file exists."""
        config_file = Path("map_locations_ai/config.yaml")
        assert config_file.exists()

    def test_agent_prompt_exists(self):
        """Test that agent prompt file exists."""
        prompt_file = Path("map_locations_ai/agent_prompt.txt")
        assert prompt_file.exists()

    def test_config_structure(self):
        """Test that config has expected structure."""
        pipeline = LocationExtractionPipeline("map_locations_ai/config.yaml")
        config = pipeline.config

        # Check LLM settings
        assert "model" in config["llm"]
        assert "temperature" in config["llm"]
        assert "max_tokens" in config["llm"]
        assert "timeout" in config["llm"]

        # Check processing settings
        assert "chunk_size" in config["processing"]
        assert "overlap_size" in config["processing"]

        # Check output settings
        assert "temp_dir" in config["output"]
        assert "trace_dir" in config["output"]
        assert "chunk_prefix" in config["output"]


class TestAIPackageStructure:
    """Test AI package structure and organization."""

    def test_package_structure(self):
        """Test that package has expected structure."""
        ai_package_dir = Path("map_locations_ai")
        assert ai_package_dir.exists()
        assert (ai_package_dir / "pipeline.py").exists()
        assert (ai_package_dir / "config.yaml").exists()
        assert (ai_package_dir / "agent_prompt.txt").exists()

    def test_temp_directories_exist(self):
        """Test that temp directories exist."""
        temp_dir = Path("map_locations_ai/temp")
        trace_dir = Path("map_locations_ai/trace")

        # These should be created by the pipeline
        assert temp_dir.exists()
        assert trace_dir.exists()

    def test_documentation_exists(self):
        """Test that documentation exists."""
        docs_dir = Path("docs")
        assert docs_dir.exists()
        assert (docs_dir / "ai-agent-guide.md").exists()
        assert (docs_dir / "implementation-status.md").exists()
