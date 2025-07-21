#!/usr/bin/env python3
"""
Custom build script for the AI package that avoids file moving.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path


def build_ai_package():
    """Build the AI package using a temporary pyproject.toml."""

    # Get the project root
    project_root = Path(__file__).parent.parent
    ai_pyproject = project_root / "map_locations_ai" / "pyproject.toml"

    if not ai_pyproject.exists():
        print("❌ AI package pyproject.toml not found")
        return False

    # Create a temporary directory for the build
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        # Copy the AI package pyproject.toml to the temp directory
        temp_pyproject = temp_dir_path / "pyproject.toml"
        shutil.copy2(ai_pyproject, temp_pyproject)

        # Copy the AI package directory to the temp directory
        ai_src = project_root / "map_locations_ai"
        ai_dest = temp_dir_path / "map_locations_ai"
        shutil.copytree(ai_src, ai_dest)

        # Copy necessary files from the main project
        for file_name in ["LICENSE", "MANIFEST.in", "README.md"]:
            src_file = project_root / file_name
            if src_file.exists():
                shutil.copy2(src_file, temp_dir_path)

        # Change to the temp directory and build
        original_cwd = os.getcwd()
        os.chdir(temp_dir)

        try:
            # Run the build
            result = subprocess.run(
                [sys.executable, "-m", "build"],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print("✅ AI package built successfully")

                # Copy the built packages to the main dist directory
                main_dist = project_root / "dist"
                main_dist.mkdir(exist_ok=True)

                temp_dist = temp_dir_path / "dist"
                if temp_dist.exists():
                    for file_path in temp_dist.glob("*"):
                        shutil.copy2(file_path, main_dist)
                    print(f"📦 Built packages copied to {main_dist}")

                return True
            else:
                print(f"❌ Build failed: {result.stderr}")
                return False

        finally:
            os.chdir(original_cwd)


if __name__ == "__main__":
    success = build_ai_package()
    sys.exit(0 if success else 1)
