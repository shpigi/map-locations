#!/bin/bash

# Development Environment Setup Script for Map Locations
# This script sets up the development environment with pre-commit hooks

set -e

echo "🚀 Setting up Map Locations development environment..."

# Check if we're in the right directory
if [ ! -f "setup.py" ] || [ ! -f "map_locations/core.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Warning: No virtual environment detected"
    echo "   Consider creating and activating a virtual environment first:"
    echo "   python -m venv venv"
    echo "   source venv/bin/activate  # On Linux/Mac"
    echo "   venv\\Scripts\\activate     # On Windows"
    echo ""
fi

# Install the package in development mode
echo "📦 Installing package in development mode..."
pip install -e ".[dev]"

# Install pre-commit hooks
echo "🔧 Installing pre-commit hooks..."
pre-commit install

# Run initial pre-commit checks
echo "🔍 Running initial pre-commit checks..."
pre-commit run --all-files

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   - Make your changes"
echo "   - Run 'pre-commit run' to check staged files"
echo "   - Run 'pre-commit run --all-files' to check all files"
echo "   - Commit your changes: git commit -m 'feat: your message'"
echo ""
echo "📚 Useful commands:"
echo "   make test          # Run tests"
echo "   make lint          # Run pre-commit checks on all files"
echo "   make lint-staged   # Run pre-commit checks on staged files"
echo "   make format        # Format code"
echo "   pre-commit run     # Run pre-commit on staged files"
echo ""
