"""
Minimal tests for example files to ensure they run without errors.
"""

import subprocess
import sys
from pathlib import Path

import pytest


class TestExamples:
    """Test that example files run without errors."""

    def test_basic_usage_example_runs(self) -> None:
        """Test that basic_usage.py runs without errors."""
        examples_dir = Path(__file__).parent.parent / "examples"
        example_file = examples_dir / "basic_usage.py"

        # Skip if example file doesn't exist
        if not example_file.exists():
            pytest.skip("basic_usage.py example file not found")

        # Run the example
        result = subprocess.run(
            [sys.executable, str(example_file)], capture_output=True, text=True, cwd=examples_dir
        )

        # Check that it ran successfully
        assert result.returncode == 0, f"Example failed with error: {result.stderr}"

    def test_google_maps_example_runs(self) -> None:
        """Test that google_maps_example.py runs without errors."""
        examples_dir = Path(__file__).parent.parent / "examples"
        example_file = examples_dir / "google_maps_example.py"

        # Skip if example file doesn't exist
        if not example_file.exists():
            pytest.skip("google_maps_example.py example file not found")

        # Skip if passages.yaml doesn't exist (required by the example)
        passages_file = Path(__file__).parent.parent / "passages.yaml"
        if not passages_file.exists():
            pytest.skip("passages.yaml file not found (required for google_maps_example.py)")

        # Run the example
        result = subprocess.run(
            [sys.executable, str(example_file)], capture_output=True, text=True, cwd=examples_dir
        )

        # Check that it ran successfully
        assert result.returncode == 0, f"Example failed with error: {result.stderr}"
