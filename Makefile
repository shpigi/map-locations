.PHONY: help install install-dev install-all test lint format clean build publish \
         install-main install-ai \
         test-main test-ai test-all test-fast test-pre-commit test-staged \
         lint-main lint-ai lint-strict lint-ai-strict \
         format-main format-ai \
         build-main build-ai \
         setup-dev-full setup-dev-main setup-dev-ai \
         pre-commit pre-commit-quick pre-commit-code pre-commit-fast pre-commit-check pre-commit-full pre-commit-with-tests \
         check-clean clean-all version

# Default target
help:
	@echo "🚀 Map Locations Development Commands"
	@echo ""
	@echo "📦 PACKAGE MANAGEMENT:"
	@echo "  install           - Install main package in development mode"
	@echo "  install-dev       - Install main package with dev dependencies"
	@echo "  install-all       - Install all packages (main, ai) in development mode"
	@echo "  install-main      - Install main package only"
	@echo "  install-ai        - Install AI package only"
	@echo ""
	@echo "🧪 TESTING:"
	@echo "  test              - Run tests for main package"
	@echo "  test-all          - Run tests for all packages"
	@echo "  test-fast         - Run essential tests only (quick feedback)"
	@echo "  test-pre-commit   - Run lightweight tests for pre-commit hooks"
	@echo "  test-staged       - Test only if test files are staged"
	@echo "  test-main         - Run tests for main package"
	@echo "  test-ai           - Run tests for AI package"
	@echo ""
	@echo "🔍 CODE QUALITY:"
	@echo "  lint              - Run linting for all packages (lenient AI mode)"
	@echo "  lint-strict       - Run strict linting for all packages (no lenient mode)"
	@echo "  lint-staged       - Run pre-commit checks on staged files only"
	@echo "  lint-main         - Run linting for main package"
	@echo "  lint-ai           - Run linting for AI package (lenient mode)"
	@echo "  lint-ai-strict    - Run strict linting for AI package"
	@echo "  format            - Format code for all packages"
	@echo "  format-main       - Format main package code"
	@echo "  format-ai         - Format AI package code"
	@echo ""
	@echo "🏗️  BUILD & PUBLISH:"
	@echo "  build             - Build all packages"
	@echo "  build-main        - Build main package"
	@echo "  build-ai          - Build AI package"
	@echo "  publish-test      - Publish all packages to Test PyPI"
	@echo "  publish-prod      - Publish all packages to Production PyPI"
	@echo ""
	@echo "🔧 DEVELOPMENT SETUP:"
	@echo "  setup-dev-full    - Full development setup (all packages + tools)"
	@echo "  setup-dev-main    - Setup for main package development"
	@echo "  setup-dev-ai      - Setup for AI package development"
	@echo ""
	@echo "🔍 PRE-COMMIT TESTING:"
	@echo "  pre-commit        - Standard pre-commit check (recommended)"
	@echo "  pre-commit-quick  - Fast pre-commit for frequent commits (no tests)"
	@echo "  pre-commit-code   - Code-only check (format + lint, no tests)"
	@echo "  pre-commit-fast   - Minimal pre-commit with fast tests"
	@echo "  pre-commit-full   - Full pre-commit check (comprehensive)"
	@echo "  check-clean       - Check if working directory is clean"
	@echo ""
	@echo "🧹 CLEANUP:"
	@echo "  clean             - Clean build artifacts for all packages"
	@echo "  clean-all         - Deep clean (includes cache files)"
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

# Install all packages in development mode
install-all: install-main install-ai



# Install main package only
install-main:
	@echo "📦 Installing main package..."
	pip install -e .

# Install AI package only
install-ai: install-main
	@echo "📦 Installing AI package..."
	pip install -e map_locations_ai/

# =============================================================================
# DEVELOPMENT SETUP TARGETS
# =============================================================================

# Full development setup with all packages and tools
setup-dev-full: install-all
	@echo "🔧 Setting up full development environment..."
	pip install pre-commit twine build
	pre-commit install
	@echo "✅ Full development environment ready!"

# Setup for main package development only
setup-dev-main: install-dev
	@echo "🔧 Setting up main package development..."
	pre-commit install
	@echo "✅ Main package development environment ready!"

# Setup for AI package development
setup-dev-ai: install-main install-ai
	@echo "🔧 Setting up AI package development..."
	pip install pre-commit pytest pytest-cov black isort mypy
	pre-commit install
	@echo "✅ AI package development environment ready!"

# =============================================================================
# TESTING TARGETS
# =============================================================================

# Run tests for main package (backward compatibility)
test:
	@echo "🧪 Running main package tests..."
	pytest tests/ -v --cov=map_locations --cov-report=term-missing

# Fast tests - only run essential tests for quick feedback
test-fast:
	@echo "⚡ Running fast tests (essential only)..."
	pytest tests/ -v --tb=short -x --disable-warnings -q

# Pre-commit tests - lightweight tests suitable for pre-commit hooks
test-pre-commit:
	@echo "🔍 Running pre-commit tests..."
	pytest tests/ -v --tb=short -x --disable-warnings -q --maxfail=3

# Run tests for all packages
test-all: test-main test-ai



# Test main package
test-main:
	@echo "🧪 Testing main package..."
	pytest tests/ -v --cov=map_locations --cov-report=term-missing

# Test AI package
test-ai:
	@echo "🧪 Testing AI package..."
	@if [ -d "map_locations_ai/tests/" ]; then \
		pytest map_locations_ai/tests/ -v --cov=map_locations_ai --cov-report=term-missing; \
	else \
		echo "⚠️  No tests found for AI package"; \
	fi

# =============================================================================
# LINTING TARGETS
# =============================================================================

# Run linting for all packages
lint: lint-main lint-ai

# Run linting on staged files only
lint-staged:
	pre-commit run



# Lint main package
lint-main:
	@echo "🔍 Linting main package..."
	flake8 map_locations/ tests/ --max-line-length=100
	mypy map_locations/ --ignore-missing-imports

# Lint AI package (lenient mode for development)
lint-ai:
	@echo "🔍 Linting AI package..."
	@if [ -d "map_locations_ai/" ]; then \
		echo "  Running flake8 (lenient mode)..."; \
		flake8 map_locations_ai/ --max-line-length=100 --extend-ignore=E226,E501 || echo "⚠️  Flake8 issues found (continuing)"; \
		echo "  Running mypy (lenient mode)..."; \
		mypy map_locations_ai/ --ignore-missing-imports --disable-error-code=no-untyped-def --disable-error-code=arg-type --disable-error-code=misc || echo "⚠️  MyPy issues found (continuing)"; \
	fi

# =============================================================================
# FORMATTING TARGETS
# =============================================================================

# Format code for all packages
format: format-main format-ai



# Format main package
format-main:
	@echo "🎨 Formatting main package..."
	black map_locations/ tests/ --line-length=100
	isort map_locations/ tests/ --profile=black --line-length=100

# Format AI package
format-ai:
	@echo "🎨 Formatting AI package..."
	@if [ -d "map_locations_ai/" ]; then \
		black map_locations_ai/ --line-length=100; \
		isort map_locations_ai/ --profile=black --line-length=100; \
	fi

# =============================================================================
# BUILD TARGETS
# =============================================================================

# Build all packages
build: build-main build-ai



# Build main package
build-main: clean
	@echo "🏗️  Building main package..."
	python -m build

# Build AI package
build-ai: clean
	@echo "🏗️  Building AI package..."
	@if [ -f "map_locations_ai/pyproject.toml" ]; then \
		python scripts/build_ai.py; \
	else \
		echo "⚠️  No build configuration found for AI package"; \
	fi

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

# =============================================================================
# PUBLISHING TARGETS
# =============================================================================

# Publish all packages to Test PyPI with full checks
publish-test: test-all lint build
	@echo "🚀 Publishing all packages to Test PyPI..."
	./scripts/publish.sh test --skip-checks

# Publish all packages to Production PyPI with full checks
publish-prod: test-all lint build
	@echo "🚀 Publishing all packages to Production PyPI..."
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

# Test AI CLI if available
test-cli-ai:
	@echo "🧪 Testing AI CLI..."
	@if python -c "import map_locations_ai.interfaces.cli" 2>/dev/null; then \
		python -m map_locations_ai.interfaces.cli --help; \
	else \
		echo "⚠️  AI CLI not available (package not installed)"; \
	fi

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

# Strict linting for all packages (no lenient mode)
lint-strict: lint-main lint-ai-strict

# Strict linting for AI package (full error reporting)
lint-ai-strict:
	@echo "🔍 Strict linting AI package..."
	@if [ -d "map_locations_ai/" ]; then \
		flake8 map_locations_ai/ --max-line-length=100; \
		mypy map_locations_ai/ --ignore-missing-imports; \
	fi

# =============================================================================
# PRE-COMMIT TESTING OPTIONS
# =============================================================================

# Code-only pre-commit check (no tests - for work-in-progress commits)
pre-commit-code: format lint
	@echo "📝 Code-only pre-commit check complete!"

# Minimal pre-commit check (fast, essential only)
pre-commit-fast: format lint test-fast
	@echo "⚡ Fast pre-commit check complete!"

# Standard pre-commit check (includes lightweight tests)
pre-commit-check: format lint test-pre-commit
	@echo "✅ Pre-commit check complete!"

# Full pre-commit check (comprehensive but slower)
pre-commit-full: format lint test-all
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

# Standard pre-commit preparation (recommended)
pre-commit: pre-commit-check
	@echo "✅ Ready for commit!"

# Fast pre-commit for frequent commits
pre-commit-quick: pre-commit-code
	@echo "⚡ Quick pre-commit ready!"

# Fast pre-commit with tests
pre-commit-with-tests: pre-commit-fast
	@echo "⚡ Fast pre-commit with tests complete!"

# CI simulation
ci: clean install-all test-all lint-strict build
	@echo "✅ CI simulation complete!"
