# Development Guide

This document provides comprehensive information about the development setup, pre-commit hooks, and development workflow for the Map Locations project.

## 🏗️ Project Architecture

This project uses a **unified package architecture** with the AI functionality integrated into the main package:

- **`map_locations/`**: Main mapping and visualization library
- **`map_locations_ai/`**: AI module for location data curation (included in main package)

The AI module is now part of the main `map-locations` package, providing a unified installation and development experience.

## 🚀 Quick Start

### 1. Full Development Setup (Recommended)

```bash
# Clone the repository
git clone https://github.com/shpigi/map-locations.git
cd map-locations

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Complete development environment setup
make setup-dev-full
```

### 2. Package Installation

```bash
# Install package in development mode
make install

# Install with development dependencies
make install-dev
```

### 3. View All Available Commands

```bash
# See comprehensive help with all development commands
make help
```

## ⚡ Development Workflow Recommendations

Choose the workflow that matches your development style and current task:

### 🔄 Daily Development Cycle

#### **For Frequent/Quick Commits** ⚡
```bash
# Super fast - format and lint only (no tests)
make pre-commit-quick
```
**Perfect for**: Work-in-progress commits, quick saves, experimental changes, when tests are still failing.

#### **For Regular Development** ✅
```bash
# Standard workflow - format, lint, and lightweight tests
make pre-commit
```
**Perfect for**: Normal feature development, bug fixes, regular commits.

#### **For Feature Completion** 🏆
```bash
# Comprehensive - format, lint, tests, build, and CLI verification
make pre-commit-full
```
**Perfect for**: Feature completion, before pushing to main, release preparation.

### 🧪 Smart Testing Options

#### **Quick Feedback Testing**
```bash
make test-fast           # Essential tests only (stops on first failure)
make test-pre-commit     # Lightweight tests for pre-commit hooks
make test-staged         # Only test if test files are staged
```

#### **Comprehensive Testing**
```bash
make test               # Run all tests for the unified package
```

#### **Development Quality Checks**
```bash
make dev-check          # Quick format + lint + fast tests
make check-clean        # Check if working directory is clean
```

### 🎯 Recommended Workflow Patterns

#### **🔥 Hot Development** (Rapid iteration)
```bash
# Make changes...
make dev-check          # Quick quality check
# More changes...
make pre-commit-quick   # Fast commit preparation
git add . && git commit -m "WIP: feature development"
```

#### **📋 Standard Feature Work**
```bash
# Make changes...
make pre-commit         # Standard commit preparation
git add . && git commit -m "feat: implement new feature"
```

#### **🚀 Pre-Push/Release**
```bash
# Before pushing or releasing
make pre-commit-full    # Complete quality assurance
make ci                 # Simulate full CI pipeline
git push
```

## 🔍 Enhanced Pre-commit Testing

The project now supports multiple levels of pre-commit testing to match your development speed:

| Command | Speed | Checks | Use Case |
|---------|-------|---------|----------|
| `make pre-commit-quick` | ⚡ Instant | Format + Lint | Frequent commits, WIP |
| `make pre-commit` | 🚀 Fast | Format + Lint + Light Tests | Regular development |
| `make pre-commit-full` | 🧪 Thorough | Format + Lint + Tests + Build + CLI | Feature complete |

### Smart File Detection

```bash
# Only runs tests if test files are in staging area
make test-staged

# Check git status and working directory cleanliness
make check-clean
```

## Pre-commit Hooks

This project uses pre-commit hooks to enforce code quality standards:

### Code Quality Hooks

- **Black**: Code formatting with 100-character line length
- **isort**: Import sorting with Black profile
- **Flake8**: Style checking with project-specific rules
- **MyPy**: Type checking with appropriate configurations

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

### Optional Testing Hook

```yaml
# Uncomment in .pre-commit-config.yaml to enable automatic testing on commits
- repo: local
  hooks:
    - id: pytest-fast
      name: pytest-fast
      entry: pytest
      language: python
      args: [tests/, -v, --tb=short, -x]
      files: ^(tests/|map_locations/)
      pass_filenames: false
```

## Code Style Standards

### Line Length
- **Maximum**: 100 characters (project standard)
- **Rationale**: Allows for readable code on modern wide screens while maintaining readability

### Linting

The project supports different linting levels:

```bash
# Standard linting (recommended for development)
make lint               # Standard linting for all code

# Lint only staged files
make lint-staged        # Run pre-commit checks on staged files only
```

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
from map_locations.common import Location, LocationList
```

### Type Annotations
```python
# Use common models when possible
from map_locations.common import Location, LocationList

def process_locations(locations: LocationList) -> set[str]:
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
def export_to_json(locations: LocationList, output_path: str) -> None:
    """Export locations to JSON format.

    Args:
        locations: List of location dictionaries
        output_path: Path to save the JSON file

    Raises:
        FileNotFoundError: If output directory doesn't exist
    """
```

## Development Workflow

### 1. Making Changes

```bash
# Create a feature branch
git checkout -b feature/amazing-feature

# Make your changes
# ... edit files ...

# Choose your commit preparation level:

# Option A: Quick commits (format + lint only)
make pre-commit-quick

# Option B: Standard commits (with lightweight tests)
make pre-commit

# Option C: Comprehensive commits (full quality checks)
make pre-commit-full

# If checks pass, commit your changes
git add . && git commit -m "feat: add amazing feature"

# Push changes
git push origin feature/amazing-feature
```

### 2. Unified Package Development

```bash
# Work on the unified package
make install
make format
make test

# Test specific functionality
make test-cli          # Test CLI functionality
make test-fast         # Quick test feedback
```

### 3. Running Checks Manually

```bash
# Format all code
make format

# Lint with appropriate levels
make lint            # Standard linting
make lint-staged     # Lint only staged files

# Testing options
make test-fast       # Quick feedback
make test            # Comprehensive
make test-pre-commit # Lightweight for commits
```

### 4. Fixing Issues

If pre-commit hooks fail:

1. **Black/isort failures**: Run `make format` to auto-fix
2. **Flake8 failures**: Fix style issues manually
3. **MyPy failures**: Fix type annotation issues
4. **Test failures**: Use `make test-fast` for quick feedback, fix issues incrementally

## Testing

### Multi-Speed Testing Strategy

```bash
# 🚀 For quick feedback during development
make test-fast           # Essential tests, stops on first failure

# ✅ For regular development workflow
make test-pre-commit     # Lightweight tests suitable for commits

# 🏆 For comprehensive quality assurance
make test               # Complete test suite

# 🔍 Smart testing based on staged files
make test-staged        # Only run if test files are staged
```

### Writing Tests

- Place tests in the `tests/` directory
- Use descriptive test names that explain the behavior
- Test both success and failure cases
- Mock external dependencies (especially for AI functionality)
- Use pytest fixtures for common setup
- Follow the shared data models for consistency

## Build and Packaging

### Building Package

```bash
# Build the unified package
make build
```

### Publishing

```bash
# Test publishing (recommended)
make publish-test       # Publish to Test PyPI

# Production publishing
make publish-prod       # Publish to Production PyPI
```

## Code Quality Commands

### Formatting
```bash
make format             # Format all code
```

### Linting
```bash
make lint              # Standard linting
make lint-staged       # Lint only staged files
```

### Development Shortcuts
```bash
make dev-check         # Quick: format + lint + fast tests
make ci               # Full CI simulation locally
```

## Troubleshooting

### Pre-commit Issues

1. **Hooks not running**: Reinstall hooks
   ```bash
   pre-commit install --overwrite
   ```

2. **Hook failures**: Check specific error and choose appropriate fix level
   ```bash
   make pre-commit-quick    # Skip tests if they're failing
   make pre-commit          # Standard checks
   ```

### MyPy Issues

1. **Type annotation errors**: Fix type hints or add appropriate ignores
2. **Import errors**: Add proper type stub packages
3. **Union type issues**: Handle None cases properly

### Test Issues

1. **Slow tests**: Use fast mode for development
   ```bash
   make test-fast         # Quick feedback
   ```

2. **Test failures**: Debug incrementally
   ```bash
   make test-fast         # Quick feedback
   pytest tests/ -k "test_name"  # Run specific test
   ```

### Setup Issues

1. **Installation issues**: Clean and reinstall
   ```bash
   make clean-all         # Deep clean
   make setup-dev-full    # Fresh install
   ```

## IDE Configuration

### VS Code

Add to `.vscode/settings.json`:
```json
{
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.flake8Args": ["--max-line-length=100"],
    "editor.rulers": [100],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    },
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

### PyCharm

1. Install Black and isort plugins
2. Configure Black as external tool with `--line-length=100`
3. Set project line length to 100 characters
4. Enable auto-formatting on save
5. Configure pytest as default test runner

## Continuous Integration

The project uses GitHub Actions for CI/CD:

- **Package Installation**: Tests installation and dependencies
- **Multi-level Testing**: Runs different test suites
- **Quality Checks**: Runs appropriate linting
- **Coverage Reporting**: Aggregates coverage across the package
- **Building**: Builds and validates the package

## Version Management

```bash
# Check current version
make version

# Update version
make version-update VERSION=0.1.4

# Semantic versioning
make version-patch      # 0.1.2 → 0.1.3
make version-minor      # 0.1.2 → 0.2.0
make version-major      # 0.1.2 → 1.0.0
```

## Contributing

1. **Fork** the repository
2. **Setup** development environment: `make setup-dev-full`
3. **Create** a feature branch: `git checkout -b feature/amazing-feature`
4. **Develop** with appropriate workflow:
   - Use `make pre-commit-quick` for frequent commits
   - Use `make pre-commit` for regular development
   - Use `make pre-commit-full` before pushing
5. **Test** your changes: `make test`
6. **Update** documentation if needed
7. **Submit** a pull request

### Contribution Guidelines

- Follow the unified package architecture
- Use appropriate linting levels
- Write tests for new functionality
- Update documentation for significant changes
- Use semantic commit messages
- Ensure the package builds successfully

## 📚 Resources

- **Pre-commit**: [Documentation](https://pre-commit.com/)
- **Code Quality**:
  - [Black](https://black.readthedocs.io/)
  - [Flake8](https://flake8.pycqa.org/)
  - [MyPy](https://mypy.readthedocs.io/)
- **Testing**: [Pytest Documentation](https://docs.pytest.org/)
- **Packaging**: [Python Packaging Guide](https://packaging.python.org/)
- **Git**: [Conventional Commits](https://www.conventionalcommits.org/)
- **Types**: [Python Type Hints](https://docs.python.org/3/library/typing.html)

## 🎯 Quick Reference

### Most Common Commands
```bash
# Setup
make setup-dev-full      # Complete development setup

# Daily Development
make dev-check          # Quick quality check
make pre-commit         # Standard commit prep
make pre-commit-quick   # Fast commit prep

# Testing
make test-fast          # Quick testing
make test               # Full testing

# Quality
make format             # Format all code
make lint               # Lint all code
```

### Speed vs Quality Matrix

| Speed | Command | Checks | Best For |
|-------|---------|---------|----------|
| ⚡ Fastest | `make pre-commit-quick` | Format + Lint | WIP commits |
| 🚀 Fast | `make pre-commit` | Format + Lint + Light Tests | Regular development |
| 🔧 Thorough | `make pre-commit-full` | Format + Lint + Tests + Build + CLI | Feature completion |
| 🏭 Complete | `make ci` | Full build pipeline | Pre-push validation |
