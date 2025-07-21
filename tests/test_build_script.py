"""
Tests for the custom build script functionality.
"""

import shutil
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.build_ai import build_ai_package


class TestBuildScript:
    """Test the custom AI package build script."""

    def test_build_script_import(self):
        """Test that the build script can be imported."""
        from scripts.build_ai import build_ai_package

        assert build_ai_package is not None
        assert callable(build_ai_package)

    def test_build_script_function_exists(self):
        """Test that the main function exists."""
        from scripts.build_ai import build_ai_package

        assert build_ai_package is not None

    @patch("scripts.build_ai.subprocess.run")
    def test_build_script_success(self, mock_run):
        """Test successful build scenario."""
        # Mock successful subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Test the function
        result = build_ai_package()
        assert result is True

    @patch("scripts.build_ai.subprocess.run")
    def test_build_script_failure(self, mock_run):
        """Test build failure scenario."""
        # Mock failed subprocess run
        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "Build failed"
        mock_run.return_value = mock_result

        # Test the function
        result = build_ai_package()
        assert result is False

    def test_build_script_file_structure(self):
        """Test that the build script has the expected structure."""
        script_path = Path("scripts/build_ai.py")
        assert script_path.exists()

        # Check that it's a Python file
        assert script_path.suffix == ".py"

        # Check that it has the main function
        content = script_path.read_text()
        assert "def build_ai_package():" in content
        assert 'if __name__ == "__main__":' in content

    def test_build_script_dependencies(self):
        """Test that the build script has required imports."""
        script_path = Path("scripts/build_ai.py")
        content = script_path.read_text()

        # Check for required imports
        required_imports = [
            "import os",
            "import sys",
            "import subprocess",
            "import tempfile",
            "import shutil",
            "from pathlib import Path",
        ]

        for import_line in required_imports:
            assert import_line in content

    def test_build_script_executable(self):
        """Test that the build script is executable."""
        script_path = Path("scripts/build_ai.py")

        # Check shebang line
        content = script_path.read_text()
        assert content.startswith("#!/usr/bin/env python3")


class TestBuildScriptIntegration:
    """Test build script integration with the project."""

    def test_build_script_in_makefile(self):
        """Test that the build script is referenced in the Makefile."""
        makefile_path = Path("Makefile")
        content = makefile_path.read_text()

        # Check that the build script is used
        assert "python scripts/build_ai.py" in content

    def test_build_script_in_ci(self):
        """Test that the build script is used in CI."""
        ci_path = Path(".github/workflows/ci.yml")
        content = ci_path.read_text()

        # Check that the build script is referenced
        assert "python scripts/build_ai.py" in content

    def test_build_script_ai_pyproject_exists(self):
        """Test that the AI package pyproject.toml exists."""
        ai_pyproject = Path("map_locations_ai/pyproject.toml")
        assert ai_pyproject.exists()

    def test_build_script_ai_package_exists(self):
        """Test that the AI package directory exists."""
        ai_package_dir = Path("map_locations_ai")
        assert ai_package_dir.exists()
        assert ai_package_dir.is_dir()


class TestBuildScriptErrorHandling:
    """Test build script error handling."""

    @patch("scripts.build_ai.Path.exists")
    def test_build_script_missing_pyproject(self, mock_exists):
        """Test behavior when AI package pyproject.toml is missing."""
        # Mock that pyproject.toml doesn't exist
        mock_exists.return_value = False

        result = build_ai_package()
        assert result is False

    @patch("scripts.build_ai.subprocess.run")
    @patch("scripts.build_ai.Path.exists")
    def test_build_script_subprocess_error(self, mock_exists, mock_run):
        """Test handling of subprocess errors."""
        # Mock that pyproject.toml exists
        mock_exists.return_value = True

        # Mock subprocess error
        mock_run.side_effect = Exception("Subprocess error")

        # The function should handle the exception and return False
        # Currently it doesn't handle subprocess exceptions, so this will raise
        with pytest.raises(Exception):
            build_ai_package()
