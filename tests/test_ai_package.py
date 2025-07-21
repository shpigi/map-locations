"""
Tests for the AI package functionality.
"""

from pathlib import Path

import pytest

from map_locations_ai import LocationPipeline


class TestAIPackage:
    """Test AI package basic functionality."""

    def test_ai_package_import(self):
        """Test that the AI package can be imported."""
        from map_locations_ai import LocationPipeline

        assert LocationPipeline is not None

    def test_pipeline_initialization(self):
        """Test that the LocationPipeline can be initialized."""
        pipeline = LocationPipeline()
        assert pipeline is not None
        assert hasattr(pipeline, "config")

    def test_pipeline_with_config(self):
        """Test pipeline initialization with configuration."""
        config = {"test": True}
        pipeline = LocationPipeline(config=config)
        assert pipeline.config == config

    def test_pipeline_methods_exist(self):
        """Test that pipeline methods exist."""
        pipeline = LocationPipeline()
        assert hasattr(pipeline, "process_text")
        assert hasattr(pipeline, "process_urls")

    def test_process_text_returns_list(self):
        """Test that process_text returns a list."""
        pipeline = LocationPipeline()
        result = pipeline.process_text("Test text")
        assert isinstance(result, list)

    def test_process_urls_returns_list(self):
        """Test that process_urls returns a list."""
        pipeline = LocationPipeline()
        result = pipeline.process_urls(["https://example.com"])
        assert isinstance(result, list)

    def test_ai_package_version(self):
        """Test that the AI package has a version."""
        from map_locations_ai import __version__

        assert __version__ is not None
        assert isinstance(__version__, str)
        assert len(__version__) > 0


class TestAIPackageCLI:
    """Test AI package CLI functionality."""

    def test_cli_import(self):
        """Test that CLI can be imported."""
        from map_locations_ai.interfaces import cli

        assert cli is not None

    def test_cli_main_exists(self):
        """Test that CLI main function exists."""
        from map_locations_ai.interfaces.cli import main

        assert main is not None
        assert callable(main)


class TestAIPackageInterfaces:
    """Test AI package interfaces."""

    def test_web_interface_import(self):
        """Test that web interface can be imported."""
        try:
            from map_locations_ai.interfaces import web_app

            assert web_app is not None
        except ImportError:
            # Skip if gradio is not installed (optional dependency)
            pytest.skip("gradio not installed (optional dependency)")

    def test_agent_components_import(self):
        """Test that agent components can be imported."""
        from map_locations_ai.agent import enrichers, extractors, validators

        assert extractors is not None
        assert enrichers is not None
        assert validators is not None


class TestAIPackageStructure:
    """Test AI package structure and organization."""

    def test_package_structure(self):
        """Test that the AI package has the expected structure."""
        ai_package_dir = Path("map_locations_ai")

        # Check main directories exist
        assert (ai_package_dir / "agent").exists()
        assert (ai_package_dir / "interfaces").exists()
        assert (ai_package_dir / "data_sources").exists()
        assert (ai_package_dir / "evaluation").exists()
        assert (ai_package_dir / "utils").exists()

    def test_agent_components_exist(self):
        """Test that agent components exist."""
        agent_dir = Path("map_locations_ai/agent")

        # Check agent files exist
        assert (agent_dir / "pipeline.py").exists()
        assert (agent_dir / "extractors.py").exists()
        assert (agent_dir / "enrichers.py").exists()
        assert (agent_dir / "validators.py").exists()

    def test_interfaces_exist(self):
        """Test that interface files exist."""
        interfaces_dir = Path("map_locations_ai/interfaces")

        # Check interface files exist
        assert (interfaces_dir / "cli.py").exists()
        assert (interfaces_dir / "web_app.py").exists()
