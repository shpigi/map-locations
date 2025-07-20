.PHONY: help install install-dev test lint format clean build publish

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install the package in development mode"
	@echo "  install-dev  - Install the package with development dependencies"
	@echo "  test         - Run tests"
	@echo "  lint         - Run pre-commit checks on all files"
	@echo "  lint-staged  - Run pre-commit checks on staged files only"
	@echo "  format       - Format code with black and isort"
	@echo "  clean        - Clean build artifacts"
	@echo "  build        - Build the package"
	@echo "  publish      - Build and publish to PyPI (if configured)"
	@echo "  publish-test - Publish to Test PyPI with full checks"
	@echo "  publish-prod - Publish to Production PyPI with full checks"
	@echo "  publish-test-quick - Publish to Test PyPI without checks"
	@echo "  publish-prod-quick - Publish to Production PyPI without checks"

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
	pre-commit run --all-files

# Run linting on staged files only
lint-staged:
	pre-commit run

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

# Publish to Test PyPI with full checks (recommended)
publish-test: test lint test-cli
	./scripts/publish.sh test --skip-checks

# Publish to Production PyPI with full checks
publish-prod: test lint test-cli
	./scripts/publish.sh prod --skip-checks

# Publish to Test PyPI without checks (quick)
publish-test-quick:
	./scripts/publish.sh test --skip-checks

# Publish to Production PyPI without checks (quick)
publish-prod-quick:
	./scripts/publish.sh prod --skip-checks

# Development setup
setup-dev: install-dev
	pre-commit install

# Quick test of the CLI
test-cli:
	python -m map_locations.cli --help
