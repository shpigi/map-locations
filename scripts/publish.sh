#!/bin/bash

# Publish script for map-locations package
# Usage: ./scripts/publish.sh [test|prod] [--skip-checks]

set -e

echo "🚀 Map Locations Package Publisher"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: Not in the map-locations project directory"
    exit 1
fi

# Parse arguments
SKIP_CHECKS=false
TARGET=${1:-test}

if [ "$1" = "--skip-checks" ]; then
    SKIP_CHECKS=true
    TARGET=${2:-test}
elif [ "$2" = "--skip-checks" ]; then
    SKIP_CHECKS=true
fi

echo "🎯 Target: $TARGET"
echo "🔍 Skip checks: $SKIP_CHECKS"
echo ""

# Pre-publish checks (unless skipped)
if [ "$SKIP_CHECKS" = false ]; then
    echo "🔍 Running pre-publish checks using make commands..."
    echo ""

    # Run tests using make
    echo "🧪 Running tests (make test)..."
    if ! make test; then
        echo "❌ Tests failed! Fix tests before publishing."
        exit 1
    fi
    echo "✅ Tests passed"
    echo ""

    # Run linting using make
    echo "🔍 Running linting (make lint)..."
    if ! make lint; then
        echo "❌ Linting failed! Fix issues before publishing."
        exit 1
    fi
    echo "✅ Linting passed"
    echo ""

    # Test CLI functionality
    echo "🖥️  Testing CLI functionality..."
    if ! make test-cli; then
        echo "❌ CLI test failed!"
        exit 1
    fi
    echo "✅ CLI functionality OK"
    echo ""

    echo "✅ All pre-publish checks passed!"
    echo ""
else
    echo "⚠️  Skipping pre-publish checks (--skip-checks flag used)"
    echo ""
fi

# Build the package using make
echo "📦 Building package (make build)..."
make build
echo "✅ Package built successfully"
echo ""

# Check the built package
echo "🔍 Checking package with twine..."
if ! twine check dist/*; then
    echo "❌ Package validation failed!"
    exit 1
fi
echo "✅ Package validation passed"
echo ""

# Determine target and publish
if [ "$TARGET" = "prod" ]; then
    echo "📤 Publishing to PyPI (production)..."
    echo "⚠️  This will publish to the main PyPI repository!"
    echo "   Make sure you have a PyPI account and API token."
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading to PyPI..."
        if twine upload dist/*; then
            echo "✅ Published to PyPI!"
            echo "📦 Install with: pip install map-locations"
        else
            echo "❌ Upload failed!"
            exit 1
        fi
    else
        echo "❌ Cancelled"
        exit 1
    fi
else
    echo "📤 Publishing to Test PyPI..."
    echo "⚠️  This will publish to the test PyPI repository."
    echo "   Make sure you have a Test PyPI account and API token."
    echo ""
    read -p "Continue? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Uploading to Test PyPI..."
        if twine upload --repository testpypi dist/*; then
            echo "✅ Published to Test PyPI!"
            echo "📦 Test install with: pip install --index-url https://test.pypi.org/simple/ map-locations"
        else
            echo "❌ Upload failed!"
            exit 1
        fi
    else
        echo "❌ Cancelled"
        exit 1
    fi
fi

echo ""
echo "🎉 Done! Your package is now available for installation."
echo ""
echo "📋 Summary:"
echo "   - Target: $TARGET"
echo "   - Checks run: $([ "$SKIP_CHECKS" = false ] && echo "Yes" || echo "No")"
echo "   - Package: map-locations"
echo "   - Version: $(grep '^version =' pyproject.toml | cut -d'"' -f2)"
