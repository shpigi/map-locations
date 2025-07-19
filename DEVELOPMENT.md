# Development Guide

This document provides comprehensive information about the development setup, pre-commit hooks, and development workflow for the Map Locations project.

## Quick Start

### 1. Set up the development environment

```bash
# Clone the repository
git clone https://github.com/shpigi/map-locations.git
cd map-locations

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install with development dependencies
make install-dev

# Set up pre-commit hooks
make setup-dev
```

### 2. Run the setup script (alternative)

```bash
# Run the automated setup script
./scripts/setup-dev.sh
```

## Pre-commit Hooks

This project uses pre-commit hooks to enforce code quality standards. The hooks run automatically on every commit and include:

### Code Quality Hooks

- **Black**: Code formatting with 100-character line length
- **isort**: Import sorting with Black profile
- **Flake8**: Style checking with 100-character line length
- **MyPy**: Type checking with strict settings

### File Quality Hooks

- **trailing-whitespace**: Remove trailing whitespace
- **end-of-file-fixer**: Ensure files end with newline
- **check-yaml**: Validate YAML files
- **check-json**: Validate JSON files
- **check-toml**: Validate TOML files
- **check-case-conflict**: Detect case conflicts in filenames
- **check-docstring-first**: Ensure docstrings come first
- **check-added-large-files**: Prevent large files from being committed
- **check-merge-conflict**: Detect merge conflict markers
- **debug-statements**: Detect debug statements
- **detect-private-key**: Detect private keys in code
- **requirements-txt-fixer**: Fix requirements.txt formatting



## Code Style Standards

### Line Length
- **Maximum**: 100 characters (project standard)
- **Rationale**: Allows for readable code on modern wide screens

### Import Organization
```python
# Standard library imports
import os
from pathlib import Path
from typing import List, Dict, Any

# Third-party imports
import folium
import yaml

# Local imports
from map_locations.core import load_locations_from_yaml
```

### Type Annotations
```python
# Use typing imports for complex types
from typing import List, Dict, Set, Any

def process_locations(locations: List[Dict[str, Any]]) -> Set[str]:
    """Process locations and return unique names."""
    return {loc['name'] for loc in locations}
```

### String Formatting
```python
# ✅ Use f-strings when interpolating variables
print(f"📍 Loaded {len(locations)} locations")

# ✅ Use regular strings when no interpolation needed
print("✅ Export completed successfully!")
```

### Docstrings
```python
def export_to_json(locations: List[Dict[str, Any]], output_path: str) -> None:
    """Export locations to JSON format.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the JSON file
    """
```

## Development Workflow

### 1. Making Changes

```bash
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# ... edit files ...

# Stage your changes
git add .

# Run pre-commit checks on staged files
pre-commit run

# If checks pass, commit your changes
git commit -m "Add amazing feature"
```

### 2. Running Checks Manually

```bash
# Run all pre-commit hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run black
pre-commit run flake8
pre-commit run mypy

# Run hooks on staged files only
pre-commit run
```

### 3. Fixing Issues

If pre-commit hooks fail:

1. **Black/isort failures**: Run `make format` to auto-fix
2. **Flake8 failures**: Fix style issues manually
3. **MyPy failures**: Fix type annotation issues
4. **Other failures**: Address the specific issue mentioned



## Testing

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
pytest tests/ -v --cov=map_locations --cov-report=html

# Run specific test file
pytest tests/test_core.py -v

# Run tests with verbose output
pytest tests/ -v
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use pytest fixtures for common setup

## Code Quality Commands

```bash
# Format code
make format

# Run linting (pre-commit checks on all files)
make lint

# Run linting on staged files only
make lint-staged

# Run all quality checks
make lint && make format
```

## Troubleshooting

### Pre-commit Issues

1. **Hooks not running**: Ensure hooks are installed
   ```bash
   pre-commit install
   ```

2. **Hook failures**: Check the specific error message and fix accordingly

3. **Slow hooks**: Pre-commit caches results, subsequent runs will be faster

### MyPy Issues

1. **Import errors**: Add `--ignore-missing-imports` for external libraries
2. **Type annotation errors**: Use proper typing imports
3. **Complex types**: Use `typing` module for complex type annotations

### Flake8 Issues

1. **Line too long**: Break long lines using parentheses or backslashes
2. **Unused imports**: Remove unused imports
3. **F-strings without placeholders**: Use regular strings instead

## IDE Configuration

### VS Code

Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "editor.rulers": [100],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm

1. Install Black and isort plugins
2. Configure Black as external tool
3. Set line length to 100
4. Enable auto-formatting on save

## Continuous Integration

The project uses GitHub Actions for CI/CD. The workflow includes:

- Running tests on multiple Python versions
- Code quality checks (pre-commit hooks)
- Coverage reporting
- Type checking

## Release Process

1. Update version in `pyproject.toml`
2. Update version in `map_locations/__init__.py`
3. Create release notes
4. Tag the release
5. Build and publish to PyPI

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following the code style
4. Run pre-commit checks
5. Write tests for new functionality
6. Update documentation
7. Submit a pull request

## Resources

- [Pre-commit Documentation](https://pre-commit.com/)
- [Black Documentation](https://black.readthedocs.io/)
- [Flake8 Documentation](https://flake8.pycqa.org/)
- [MyPy Documentation](https://mypy.readthedocs.io/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
