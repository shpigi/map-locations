#!/usr/bin/env python3
"""
Version Update Script for Map Locations

This script updates the version in the single source of truth: map_locations/__init__.py
Usage:
  python scripts/update_version.py <new_version>
  python scripts/update_version.py --major
  python scripts/update_version.py --minor
  python scripts/update_version.py --patch
"""

import sys
from pathlib import Path


def update_init_py(version: str) -> bool:
    """Update version in map_locations/__init__.py by finding and replacing the version line."""
    file_path = Path("map_locations/__init__.py")
    if not file_path.exists():
        print(f"❌ {file_path} not found")
        return False

    lines = file_path.read_text().splitlines()
    version_line_index = None

    # Find the __version__ line
    for i, line in enumerate(lines):
        if line.strip().startswith("__version__ = "):
            version_line_index = i
            break

    if version_line_index is None:
        print(f"❌ Could not find __version__ line in {file_path}")
        return False

    # Update the version line
    old_line = lines[version_line_index]
    lines[version_line_index] = f'__version__ = "{version}"'

    # Write back to file
    file_path.write_text("\n".join(lines) + "\n")
    print(f"✅ Updated {file_path} to version {version}")
    print(f"   Changed: {old_line.strip()}")
    print(f"   To:      {lines[version_line_index]}")
    return True


def get_current_version() -> str:
    """Get current version from map_locations/__init__.py."""
    file_path = Path("map_locations/__init__.py")
    if not file_path.exists():
        return "unknown"

    lines = file_path.read_text().splitlines()
    for line in lines:
        if line.strip().startswith("__version__ = "):
            # Extract version from: __version__ = "0.1.2"
            version = line.split("=")[1].strip().strip("\"'")
            return version

    return "unknown"


def parse_version(version: str) -> tuple:
    """Parse version string into (major, minor, patch)."""
    parts = version.split(".")
    if len(parts) != 3:
        raise ValueError(f"Invalid version format: {version}")

    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        raise ValueError(f"Invalid version format: {version}")


def increment_version(current_version: str, increment_type: str) -> str | None:
    """Increment version based on semantic versioning rules."""
    try:
        major, minor, patch = parse_version(current_version)
    except ValueError as e:
        print(f"❌ {e}")
        return None

    if increment_type == "major":
        # MAJOR version for incompatible API changes
        return f"{major + 1}.0.0"
    elif increment_type == "minor":
        # MINOR version for backwards-compatible functionality additions
        return f"{major}.{minor + 1}.0"
    elif increment_type == "patch":
        # PATCH version for backwards-compatible bug fixes
        return f"{major}.{minor}.{patch + 1}"
    else:
        print(f"❌ Unknown increment type: {increment_type}")
        return None


def validate_version(version: str) -> bool:
    """Validate version format (semantic versioning)."""
    parts = version.split(".")
    if len(parts) != 3:
        print(f"❌ Invalid version format: {version}")
        print("   Expected format: X.Y.Z (e.g., 0.1.2)")
        return False

    try:
        for part in parts:
            int(part)
    except ValueError:
        print(f"❌ Invalid version format: {version}")
        print("   All parts must be numbers (e.g., 0.1.2)")
        return False

    return True


def main() -> None:
    """Main function to update version."""
    if len(sys.argv) != 2:
        current_version = get_current_version()
        print("🚀 Map Locations Version Updater")
        print("=" * 40)
        print(f"Current version: {current_version}")
        print("")
        print("Usage:")
        print("  # Manual version update:")
        print("  python scripts/update_version.py <new_version>")
        print("")
        print("  # Automatic semantic versioning:")
        print("  python scripts/update_version.py --major    # 0.1.2 → 1.0.0")
        print("  python scripts/update_version.py --minor    # 0.1.2 → 0.2.0")
        print("  python scripts/update_version.py --patch    # 0.1.2 → 0.1.3")
        print("")
        print("Examples:")
        print("  python scripts/update_version.py 0.1.3")
        print("  python scripts/update_version.py --patch")
        print("  python scripts/update_version.py --minor")
        print("  python scripts/update_version.py --major")
        print("")
        print("Semantic Versioning Rules:")
        print("  --major: Incompatible API changes (X.0.0)")
        print("  --minor: Backwards-compatible new features (X.Y.0)")
        print("  --patch: Backwards-compatible bug fixes (X.Y.Z)")
        print("")
        print("This will update version in the single source of truth:")
        print("  - map_locations/__init__.py")
        print("")
        print("Other files (pyproject.toml, setup.py) will automatically")
        print("read the version from the package.")
        sys.exit(1)

    arg = sys.argv[1]

    # Handle automatic semantic versioning
    if arg in ["--major", "--minor", "--patch"]:
        increment_type = arg[2:]  # Remove "--"
        current_version = get_current_version()

        if current_version == "unknown":
            print("❌ Could not determine current version")
            sys.exit(1)

        new_version = increment_version(current_version, increment_type)
        if not new_version:
            sys.exit(1)

        print("🚀 Map Locations Version Updater")
        print("=" * 40)
        print(f"Current version: {current_version}")
        print(f"Increment type: {increment_type}")
        print(f"New version: {new_version}")
        print("")

    else:
        # Manual version update
        new_version = arg

        print("🚀 Map Locations Version Updater")
        print("=" * 40)

        # Validate version format
        if not validate_version(new_version):
            sys.exit(1)

        current_version = get_current_version()
        print(f"Current version: {current_version}")
        print(f"New version: {new_version}")
        print("")

    # Update the single source of truth
    if update_init_py(new_version):
        print("")
        print("✅ Version update completed successfully!")
        print("")
        print("Next steps:")
        print("  1. Review the changes:")
        print("     git diff")
        print("")
        print("  2. Build the package:")
        print("     make clean && make build")
        print("")
        print("  3. Publish to Test PyPI:")
        print("     twine upload --repository testpypi dist/*")
        print("")
        print("  4. Or use the publish script:")
        print("     make publish-test")
        print("")
        print("Note: pyproject.toml and setup.py will automatically")
        print("use the version from map_locations/__init__.py")
    else:
        print("")
        print("❌ Version update failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
