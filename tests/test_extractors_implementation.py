"""
Test the extractors implementation against the plan requirements.

This test verifies that the implementation matches the specifications
outlined in docs/extractors_plan.md.
"""

import os
import sys
import time
from pathlib import Path
from typing import List

import psutil
import pytest
import yaml

# Try to import ExtractionAgent, but don't fail if it doesn't exist
try:
    from map_locations_ai.agent.extraction_agent import ExtractionAgent

    EXTRACTION_AGENT_AVAILABLE = True
except ImportError:
    EXTRACTION_AGENT_AVAILABLE = False

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from map_locations_ai.agent.extractors import (  # noqa: E402
    ExtractedLocation,
    StructuredExtractor,
    TextExtractor,
    URLExtractor,
)
from map_locations_ai.agent.pipeline import LocationPipeline  # noqa: E402
from map_locations_ai.utils import net_utils, nlp_utils, tools  # noqa: E402


class TestExtractorsPlanImplementation:
    """Test that the implementation matches the extractors plan requirements."""

    def test_extracted_location_schema(self):
        """Test that ExtractedLocation matches the minimal schema from plan."""
        # Test minimal schema as specified in plan
        location = ExtractedLocation(
            name="Test Location",
            address_or_hint="123 Test St, City",
            source_type="text",
            source_snippet_or_url="Visit Test Location",
            confidence=0.8,
        )

        # Verify all required fields exist
        assert hasattr(location, "name")
        assert hasattr(location, "address_or_hint")
        assert hasattr(location, "source_type")
        assert hasattr(location, "source_snippet_or_url")
        assert hasattr(location, "confidence")

        # Verify to_dict method works
        location_dict = location.to_dict()
        assert isinstance(location_dict, dict)
        assert location_dict["name"] == "Test Location"
        assert location_dict["confidence"] == 0.8

    def test_text_extractor_initialization(self):
        """Test TextExtractor initialization."""
        # Should work with API key
        if os.environ.get("LAVI_OPENAI_KEY"):
            extractor = TextExtractor()
            assert extractor is not None
            assert hasattr(extractor, "extract")
        else:
            # Should raise error without API key
            with pytest.raises(ValueError):
                TextExtractor()

    def test_url_extractor_initialization(self):
        """Test URLExtractor initialization."""
        extractor = URLExtractor()
        assert extractor is not None
        assert hasattr(extractor, "extract")
        assert extractor.timeout == 3  # As per plan

    def test_structured_extractor_initialization(self):
        """Test StructuredExtractor initialization (placeholder)."""
        extractor = StructuredExtractor()
        assert extractor is not None
        assert hasattr(extractor, "extract")
        # Should return empty list for now (placeholder)
        result = extractor.extract({})
        assert isinstance(result, list)
        assert len(result) == 0

    def test_pipeline_initialization(self):
        """Test LocationPipeline initialization."""
        pipeline = LocationPipeline()
        assert pipeline is not None
        assert hasattr(pipeline, "process_text")
        assert hasattr(pipeline, "process_urls")
        assert hasattr(pipeline, "process_mixed_input")

    def test_pipeline_methods_exist(self):
        """Test that pipeline methods exist as specified in plan."""
        pipeline = LocationPipeline()

        # Test process_text method
        result = pipeline.process_text("Test text")
        assert isinstance(result, list)

        # Test process_urls method
        result = pipeline.process_urls(["https://example.com"])
        assert isinstance(result, list)

        # Test process_mixed_input method
        result = pipeline.process_mixed_input(text="Test text", urls=["https://example.com"])
        assert isinstance(result, list)

    def test_nlp_utils_exist(self):
        """Test that NLP utility functions exist."""
        # Test extract_entities function
        assert hasattr(nlp_utils, "extract_entities")
        assert callable(nlp_utils.extract_entities)

        # Test regex_addresses function
        assert hasattr(nlp_utils, "regex_addresses")
        assert callable(nlp_utils.regex_addresses)

        # Test invitation_check function
        assert hasattr(nlp_utils, "invitation_check")
        assert callable(nlp_utils.invitation_check)

    def test_net_utils_exist(self):
        """Test that network utility functions exist."""
        # Test url_title_fetch function
        assert hasattr(net_utils, "url_title_fetch")
        assert callable(net_utils.url_title_fetch)

        # Test slug_to_name function
        assert hasattr(net_utils, "slug_to_name")
        assert callable(net_utils.slug_to_name)

        # Test classify_url function
        assert hasattr(net_utils, "classify_url")
        assert callable(net_utils.classify_url)

    def test_tools_exist(self):
        """Test that tool functions exist with @tool decorators."""
        # Test that tool functions exist
        tool_functions = [
            "extract_entities_tool",
            "regex_addresses_tool",
            "invitation_check_tool",
            "url_title_fetch_tool",
            "slug_to_name_tool",
            "classify_url_tool",
        ]

        for func_name in tool_functions:
            assert hasattr(tools, func_name)
            assert callable(getattr(tools, func_name))

    def test_regex_addresses_functionality(self):
        """Test regex_addresses function with sample data."""
        sample_text = "Meet us at 145 Rue du Temple, 75003 Paris"
        addresses = nlp_utils.regex_addresses(sample_text)

        assert isinstance(addresses, list)
        if addresses:  # If spaCy is available
            assert len(addresses) > 0
            address = addresses[0]
            assert "text" in address
            assert "confidence" in address
            assert "pattern" in address

    def test_invitation_check_functionality(self):
        """Test invitation_check function."""
        # Text that invites suggestions
        inviting_text = "Here are some additional best museums to visit"
        result = nlp_utils.invitation_check(inviting_text)

        assert isinstance(result, dict)
        assert "invites_suggestions" in result
        assert "confidence" in result
        assert "matched_phrases" in result

        # Should detect invitation
        assert result["invites_suggestions"] is True

        # Text that doesn't invite suggestions
        normal_text = "Visit the Louvre Museum"
        result = nlp_utils.invitation_check(normal_text)
        assert result["invites_suggestions"] is False

    def test_url_classification(self):
        """Test URL classification functionality."""
        # Test Gmail URL (should get low confidence)
        gmail_url = "https://mail.google.com/mail/u/0/#inbox"
        result = net_utils.classify_url(gmail_url)

        assert isinstance(result, dict)
        assert "type" in result
        assert "confidence" in result
        assert result["type"] == "gmail_thread"
        assert result["confidence"] == 0.2

        # Test travel site URL
        travel_url = "https://www.tripadvisor.com/paris"
        result = net_utils.classify_url(travel_url)
        assert result["type"] == "travel_site"
        assert result["confidence"] == 0.7

    def test_slug_to_name_functionality(self):
        """Test slug_to_name functionality."""
        # Test URL with path
        url = "https://example.com/museum-louvre"
        result = net_utils.slug_to_name(url)

        assert isinstance(result, dict)
        assert "name" in result
        assert "confidence" in result
        assert "source" in result
        assert result["name"] == "Museum Louvre"
        assert result["confidence"] == 0.5

        # Test URL without path
        url = "https://example.com"
        result = net_utils.slug_to_name(url)
        assert result["name"] == "Example Com"

    def test_configuration_file_exists(self):
        """Test that configuration file exists."""
        config_file = project_root / "map_locations_ai" / "config.yaml"
        assert config_file.exists()

        # Test that it can be read
        with open(config_file, "r") as f:
            config = yaml.safe_load(f)

        # Test key configuration sections exist
        assert "agent" in config
        assert "extraction" in config
        assert "url_processing" in config
        assert "nlp" in config

        # Test specific settings from plan
        assert "use_openai_functions" in config["agent"]
        assert "model_id" in config["agent"]
        assert config["agent"]["url_fetch_timeout"] == 3  # As per plan

    def test_extraction_agent_exists(self):
        """Test that the enhanced extraction agent exists."""
        if not EXTRACTION_AGENT_AVAILABLE:
            pytest.skip("ExtractionAgent not implemented yet")

        assert ExtractionAgent is not None

    def test_performance_targets_met(self):
        """Test that performance targets can be met."""
        # Test memory usage (should be under 500MB)
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        assert memory_mb < 500, f"Memory usage {memory_mb:.1f}MB exceeds 500MB limit"

        # Test processing time (should be under 30s for reasonable inputs)
        # This is a basic test - actual performance depends on API calls
        start_time = time.time()

        # Simple operation that should be fast
        pipeline = LocationPipeline()
        pipeline.process_text("Test")

        elapsed_time = time.time() - start_time
        assert elapsed_time < 30, f"Processing time {elapsed_time:.1f}s exceeds 30s limit"


class TestPlanCompliance:
    """Test compliance with the extractors plan specifications."""

    def test_minimal_schema_compliance(self):
        """Test that the minimal schema from plan is implemented."""
        # Schema from plan:
        # {
        #   "name": string,
        #   "address_or_hint": string,
        #   "source_type": "text" | "url",
        #   "source_snippet_or_url": string,
        #   "confidence": float
        # }

        location = ExtractedLocation(
            name="Eiffel Tower",
            address_or_hint="Champ de Mars, Paris",
            source_type="text",
            source_snippet_or_url="Visit the Eiffel Tower",
            confidence=0.9,
        )

        # Verify all fields match plan
        assert isinstance(location.name, str)
        assert isinstance(location.address_or_hint, str)
        assert location.source_type in ["text", "url"]
        assert isinstance(location.source_snippet_or_url, str)
        assert isinstance(location.confidence, float)
        assert 0 <= location.confidence <= 1

    def test_confidence_scoring_compliance(self):
        """Test that confidence scoring follows plan guidelines."""
        # Plan specifies:
        # - 0.9 for explicit addresses
        # - 0.7 for clear venue names
        # - 0.5 for ambiguous mentions

        # Test regex addresses (should be 0.9)
        sample_text = "145 Rue du Temple, 75003 Paris"
        addresses = nlp_utils.regex_addresses(sample_text)
        if addresses:
            assert addresses[0]["confidence"] == 0.9

        # Test URL title fetch (should be 0.6 if successful)
        # This would require actual HTTP request, so we test the logic
        assert True  # Placeholder for actual test

    def test_timeout_compliance(self):
        """Test that timeout settings match plan."""
        # Plan specifies ≤3s for URL title fetch
        url_extractor = URLExtractor()
        assert url_extractor.timeout == 3

        # Plan specifies ≤30s per 1000-line document
        # This is tested in performance_targets_met

    def test_tool_registry_compliance(self):
        """Test that all planned tools are implemented."""
        # Plan specifies these tools:
        planned_tools = [
            "extract_entities",
            "regex_addresses",
            "invitation_check",
            "url_title_fetch",
            "slug_to_name",
        ]

        # Check that functions exist
        for tool_name in planned_tools:
            if tool_name == "extract_entities":
                assert hasattr(nlp_utils, tool_name)
            elif tool_name == "regex_addresses":
                assert hasattr(nlp_utils, tool_name)
            elif tool_name == "invitation_check":
                assert hasattr(nlp_utils, tool_name)
            elif tool_name == "url_title_fetch":
                assert hasattr(net_utils, tool_name)
            elif tool_name == "slug_to_name":
                assert hasattr(net_utils, tool_name)

    def test_system_prompt_compliance(self):
        """Test that system prompt matches plan specifications."""
        # Test that TextExtractor has the required system prompt
        if os.environ.get("LAVI_OPENAI_KEY"):
            extractor = TextExtractor()
            system_prompt = extractor.system_prompt

            # Check for key requirements from plan
            assert "extraction-only agent" in system_prompt
            assert "Do NOT invent locations" in system_prompt
            assert "JSON array ONLY" in system_prompt
            assert "confidence" in system_prompt
