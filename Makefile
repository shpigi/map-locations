.PHONY: help install install-dev test lint format clean build publish

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  install-dev  - Install the package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run linting checks"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  publish      - Build and publish to PyPI (if configured)"

# Install the package in development mode
install:
	pip install -e .

# Install with development dependencies
install-dev:
	pip install -e ".[dev]"

# Run tests
test:
	pytest tests/ -v --cov=map_locations --cov-report=term-missing

# Run linting
lint:
	flake8 map_locations/ tests/
	mypy map_locations/

# Format code
format:
	black map_locations/ tests/
	isort map_locations/ tests/

# Clean build artifacts
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build the package
build: clean
	python -m build

# Publish to PyPI (requires proper configuration)
publish: build
	twine upload dist/*

# Development setup
setup-dev: install-dev
	pre-commit install

# Quick test of the CLI
test-cli:
	python -m map_locations.cli --help
	python -m map_locations.cli map --help
	python -m map_locations.cli export --help 