"""
Tests for example scripts.
"""

import os
import subprocess
import sys
from pathlib import Path

import pytest


class TestExamples:
    """Test that example scripts run without errors."""

    def test_basic_usage_example_runs(self) -> None:
        """Test that basic_usage.py runs without errors."""
        example_path = Path("examples/basic_usage.py")
        if example_path.exists():
            result = subprocess.run(
                [sys.executable, str(example_path)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
            )
            assert result.returncode == 0, f"Example failed: {result.stderr}"

    def test_google_maps_example_runs(self) -> None:
        """Test that google_maps_example.py runs without errors."""
        example_path = Path("examples/google_maps_example.py")
        if example_path.exists():
            # Check if package is available
            try:
                import map_locations
            except ImportError:
                pytest.skip(
                    "map_locations package not available - skipping example test"
                )

            # Run with PYTHONPATH to include current directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd()) + ":" + env.get("PYTHONPATH", "")

            result = subprocess.run(
                [sys.executable, str(example_path)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                env=env,
            )
            assert result.returncode == 0, f"Example failed: {result.stderr}"

            # Check that output files were created
            output_dir = Path("maps/google_maps_example")
            if output_dir.exists():
                # Check for map files
                expected_files = [
                    "map_osm.html",
                    "map_google.html",
                    "map_satellite.html",
                ]
                for filename in expected_files:
                    file_path = output_dir / filename
                    assert file_path.exists(), f"Map file {filename} should be created"
        else:
            pytest.skip("google_maps_example.py not found")

    def test_ai_agent_example_runs(self) -> None:
        """Test that ai_agent_example.py runs without errors."""
        example_path = Path("examples/ai_agent_example.py")
        if example_path.exists():
            # Check if package is available
            try:
                import map_locations
            except ImportError:
                pytest.skip(
                    "map_locations package not available - skipping example test"
                )

            # Run with PYTHONPATH to include current directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path.cwd()) + ":" + env.get("PYTHONPATH", "")

            result = subprocess.run(
                [sys.executable, str(example_path)],
                capture_output=True,
                text=True,
                cwd=Path.cwd(),
                env=env,
            )
            assert result.returncode == 0, f"Example failed: {result.stderr}"

            # Check that output files were created
            output_dir = Path("ai_agent_examples")
            if output_dir.exists():
                # Check for basic map file
                basic_map = output_dir / "basic_map.html"
                assert basic_map.exists(), "Basic map file should be created"

                # Check for exports directory
                exports_dir = output_dir / "exports"
                if exports_dir.exists():
                    # Check for exported files
                    exported_files = list(exports_dir.glob("complete_dataset.*"))
                    assert (
                        len(exported_files) >= 4
                    ), "Should export at least 4 file formats"

                    # Check for specific formats
                    assert (exports_dir / "complete_dataset.json").exists()
                    assert (exports_dir / "complete_dataset.csv").exists()
                    assert (exports_dir / "complete_dataset.geojson").exists()
                    assert (exports_dir / "complete_dataset.kml").exists()
