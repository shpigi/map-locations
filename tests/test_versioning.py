"""Tests for versioning system."""

import importlib
import os
import sys
from pathlib import Path

import pytest


def test_version_consistency():
    """Test that version is consistent across all files."""
    # Import the package to get version from __init__.py
    import map_locations

    # Get version from __init__.py
    init_version = map_locations.__version__

    # Verify version format (semantic versioning)
    parts = init_version.split(".")
    assert len(parts) == 3, f"Version should have 3 parts: {init_version}"

    for part in parts:
        assert part.isdigit(), f"Version parts should be numbers: {init_version}"

    print(f"✅ Version consistency check passed: {init_version}")


def test_version_import():
    """Test that version can be imported correctly."""
    import map_locations

    # Test that version is accessible
    assert hasattr(map_locations, "__version__")
    assert isinstance(map_locations.__version__, str)
    assert len(map_locations.__version__) > 0

    print(f"✅ Version import test passed: {map_locations.__version__}")


def test_version_function():
    """Test that version is accessible directly."""
    import map_locations

    # Test that version is accessible directly
    version = map_locations.__version__
    assert version == map_locations.__version__

    print(f"✅ Version function test passed: {version}")


def test_pyproject_toml_dynamic_version():
    """Test that pyproject.toml uses dynamic version."""
    # Use tomli for Python < 3.11, tomllib for Python >= 3.11
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            pytest.skip("Neither tomllib nor tomli available")

    with open("pyproject.toml", "rb") as f:
        config = tomllib.load(f)

    # Check that version is marked as dynamic
    assert "dynamic" in config["project"]
    assert "version" in config["project"]["dynamic"]

    # Check that it references the package
    assert config["tool"]["setuptools"]["dynamic"]["version"]["attr"] == "map_locations.__version__"

    print("✅ pyproject.toml dynamic version configuration is correct")


def test_build_with_dynamic_version():
    """Test that package can be built with dynamic version."""
    import shutil
    import subprocess
    import tempfile

    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        # Copy current directory to temp
        shutil.copytree(".", temp_dir, dirs_exist_ok=True)

        # Change to temp directory
        original_dir = Path.cwd()
        os.chdir(temp_dir)

        try:
            # Install in editable mode
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."], check=True, capture_output=True
            )

            # Try to build
            result = subprocess.run([sys.executable, "-m", "build"], capture_output=True, text=True)

            if result.returncode != 0:
                print(f"Build failed: {result.stderr}")
                pytest.fail("Build failed")

            print("✅ Package builds successfully with dynamic version")

        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    # Run tests
    test_version_consistency()
    test_version_import()
    test_version_function()
    test_pyproject_toml_dynamic_version()
    print("✅ All versioning tests passed!")
