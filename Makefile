.PHONY: help install install-dev test lint format clean build publish \
         test-fast test-pre-commit test-staged \
         setup-dev-full \
         pre-commit pre-commit-quick pre-commit-full \
         check-clean clean-all clean-runs version

# Default target
help:
	@echo "🚀 Map Locations Development Commands"
	@echo ""
	@echo "📦 PACKAGE MANAGEMENT:"
	@echo "  install           - Install package in development mode"
	@echo "  install-dev       - Install package with dev dependencies"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  test              - Run tests for package"
	@echo "  test-fast         - Run essential tests only (quick feedback)"
	@echo "  test-pre-commit   - Run lightweight tests for pre-commit hooks"
	@echo "  test-staged       - Test only if test files are staged"
	@echo ""
	@echo "🔍 CODE QUALITY:"
	@echo "  lint              - Run linting for package"
	@echo "  lint-staged       - Run pre-commit checks on staged files only"
	@echo "  format            - Format code for package"
	@echo ""
	@echo "🏗️  BUILD & PUBLISH:"
	@echo "  build             - Build package"
	@echo "  publish-test      - Publish package to Test PyPI"
	@echo "  publish-prod      - Publish package to Production PyPI"
	@echo ""
	@echo "🔧 DEVELOPMENT SETUP:"
	@echo "  setup-dev-full    - Full development setup (package + tools)"
	@echo ""
	@echo "🔍 PRE-COMMIT TESTING:"
	@echo "  pre-commit        - Standard pre-commit check (format + lint + tests)"
	@echo "  pre-commit-quick  - Quick pre-commit (format + lint only)"
	@echo "  pre-commit-full   - Full pre-commit check (format + lint + tests + build + CLI + clean)"
	@echo "  check-clean       - Check if working directory is clean"
	@echo ""
	@echo "🧪 CLI TESTING:"
	@echo "  test-cli          - Test CLI functionality"
	@echo ""
	@echo "🧹 CLEANUP:"
	@echo "  clean             - Clean build artifacts"
	@echo "  clean-all         - Deep clean (includes cache files)"
	@echo "  clean-runs        - Clean previous AI processing runs (temp + trace)"
	@echo ""
	@echo "📊 VERSION MANAGEMENT:"
	@echo "  version           - Show current version and update commands"
	@echo "  version-update    - Update version (specify VERSION=x.y.z)"
	@echo "  version-patch     - Increment patch version"
	@echo "  version-minor     - Increment minor version"
	@echo "  version-major     - Increment major version"

# =============================================================================
# INSTALLATION TARGETS
# =============================================================================

# Install main package in development mode (backward compatibility)
install:
	pip install -e .

# Install main package with development dependencies
install-dev:
	pip install -e ".[dev]"

# =============================================================================
# DEVELOPMENT SETUP TARGETS
# =============================================================================

# Full development setup with all packages and tools
setup-dev-full: install
	@echo "🔧 Setting up full development environment..."
	pip install pre-commit twine build
	pre-commit install
	@echo "✅ Full development environment ready!"

# Setup for main package development only
setup-dev-main: install-dev
	@echo "🔧 Setting up main package development..."
	pre-commit install
	@echo "✅ Main package development environment ready!"

# =============================================================================
# TESTING TARGETS
# =============================================================================

# Run tests for main package (backward compatibility)
test:
	@echo "🧪 Running package tests..."
	pytest tests/ -v --cov=map_locations --cov=map_locations_ai --cov-report=term-missing

# Fast tests - only run essential tests for quick feedback
test-fast:
	@echo "⚡ Running fast tests (essential only)..."
	pytest tests/ -v --tb=short -x --disable-warnings -q

# Pre-commit tests - lightweight tests suitable for pre-commit hooks
test-pre-commit:
	@echo "🔍 Running pre-commit tests..."
	pytest tests/ -v --tb=short -x --disable-warnings -q --maxfail=3

# =============================================================================
# LINTING TARGETS
# =============================================================================

# Run linting for all packages
lint:
	@echo "🔍 Linting package..."
	flake8 map_locations/ map_locations_ai/ tests/
	mypy map_locations/ map_locations_ai/ --ignore-missing-imports --exclude "pipeline_old_backup.py"

# Run linting on staged files only
lint-staged:
	pre-commit run

# =============================================================================
# FORMATTING TARGETS
# =============================================================================

# Format code for all packages
format:
	@echo "🎨 Formatting package..."
	black map_locations/ map_locations_ai/ tests/
	isort map_locations/ map_locations_ai/ tests/ --profile=black

# =============================================================================
# BUILD TARGETS
# =============================================================================

# Build all packages
build: clean
	@echo "🏗️  Building package..."
	python -m build

# =============================================================================
# CLEANUP TARGETS
# =============================================================================

# Clean build artifacts for all packages
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf map_locations_ai/build/ map_locations_ai/dist/ map_locations_ai/*.egg-info/

# Deep clean including cache files
clean-all: clean
	@echo "🧹 Deep cleaning..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf .coverage

# Clean previous AI processing runs (temp + trace)
clean-runs:
	@echo "🧹 Cleaning previous AI processing runs..."
	rm -rf map_locations_ai/temp/
	rm -rf map_locations_ai/trace/
	mkdir -p map_locations_ai/temp/
	mkdir -p map_locations_ai/trace/
	@echo "✅ Previous AI processing runs cleaned!"

# =============================================================================
# PUBLISHING TARGETS
# =============================================================================

# Publish all packages to Test PyPI with full checks
publish-test: test lint build
	@echo "🚀 Publishing package to Test PyPI..."
	./scripts/publish.sh test --skip-checks

# Publish all packages to Production PyPI with full checks
publish-prod: test lint build
	@echo "🚀 Publishing package to Production PyPI..."
	./scripts/publish.sh prod --skip-checks

# Quick publish to Test PyPI without checks
publish-test-quick: build
	./scripts/publish.sh test --skip-checks

# Quick publish to Production PyPI without checks
publish-prod-quick: build
	./scripts/publish.sh prod --skip-checks

# =============================================================================
# CLI TESTING TARGETS
# =============================================================================

# Quick test of the main CLI
test-cli:
	@echo "🧪 Testing main CLI..."
	python -m map_locations.cli --help

# =============================================================================
# VERSION MANAGEMENT
# =============================================================================

# Version management
version:
	@echo "📊 Current version: $(shell python scripts/update_version.py 2>/dev/null | grep "Current version:" | cut -d: -f2 | xargs)"
	@echo ""
	@echo "To update version:"
	@echo "  # Manual version update:"
	@echo "  make version-update VERSION=0.1.4"
	@echo "  make version-update VERSION=0.2.0"
	@echo "  make version-update VERSION=1.0.0"
	@echo ""
	@echo "  # Automatic semantic versioning:"
	@echo "  make version-patch    # Increment patch version (0.1.2 → 0.1.3)"
	@echo "  make version-minor    # Increment minor version (0.1.2 → 0.2.0)"
	@echo "  make version-major    # Increment major version (0.1.2 → 1.0.0)"

version-update:
	@if [ -z "$(VERSION)" ]; then \
		echo "❌ Error: VERSION is required"; \
		echo "Usage: make version-update VERSION=0.1.4"; \
		exit 1; \
	fi
	python scripts/update_version.py $(VERSION)

version-patch:
	python scripts/update_version.py --patch

version-minor:
	python scripts/update_version.py --minor

version-major:
	python scripts/update_version.py --major

# =============================================================================
# STRICT LINTING (for production-ready code)
# =============================================================================

# =============================================================================
# PRE-COMMIT TESTING OPTIONS
# =============================================================================

# Standard pre-commit check (format + lint + tests)
pre-commit: format lint test-pre-commit
	@echo "✅ Pre-commit check complete!"

# Quick pre-commit (format + lint only, no tests)
pre-commit-quick: format lint
	@echo "⚡ Quick pre-commit ready!"

# Full pre-commit check (comprehensive)
pre-commit-full: format lint test build test-cli check-clean
	@echo "✅ Full pre-commit check complete!"

# Test only staged files (if test files are staged)
test-staged:
	@echo "🔍 Testing staged files..."
	@if git diff --cached --name-only | grep -E "(test_|tests/)" > /dev/null; then \
		echo "  Found staged test files, running tests..."; \
		make test-pre-commit; \
	else \
		echo "  No test files staged, skipping tests"; \
	fi

# Check if working directory is clean (good for pre-commit)
check-clean:
	@echo "🔍 Checking working directory..."
	@if [ -z "$(shell git status --porcelain)" ]; then \
		echo "✅ Working directory is clean"; \
	else \
		echo "⚠️  Working directory has uncommitted changes:"; \
		git status --short; \
	fi

# =============================================================================
# DEVELOPMENT WORKFLOW SHORTCUTS
# =============================================================================

# Quick development cycle: format, lint, fast test
dev-check: format lint test-fast
	@echo "✅ Development check complete!"

# CI simulation
ci: clean install test lint build
	@echo "✅ CI simulation complete!"
