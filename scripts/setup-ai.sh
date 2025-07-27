#!/bin/bash

# AI Package Setup Script for Map Locations
# This script sets up the AI package with all required dependencies

set -e

echo "🤖 Setting up Map Locations AI package..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -d "map_locations_ai" ]; then
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

# Install the main package in development mode
echo "📦 Installing main package in development mode..."
pip install -e ".[dev]"

# Install spaCy and download required model
echo "🧠 Installing spaCy and required model..."
pip install spacy>=3.5.0

# Download spaCy model
echo "📥 Downloading spaCy English model..."
python -m spacy download en_core_web_sm

# Verify spaCy installation
echo "🔍 Verifying spaCy installation..."
python -c "
import spacy
nlp = spacy.load('en_core_web_sm')
print('✅ spaCy model loaded successfully')
"

# Test AI package import
echo "🧪 Testing AI package import..."
python -c "
import map_locations_ai
print('✅ AI package imported successfully')
"

echo ""
echo "✅ AI package setup complete!"
echo ""
echo "📋 Available commands:"
echo "   python run_traced_agent.py <input_file> [region]  # Run with tracing"
echo "   python run_memory_agent.py <input_file> [region]  # Run memory agent"
echo "   python examples/memory_agent_example.py           # Run examples"
echo ""
echo "🔧 Environment variables:"
echo "   LAVI_OPENAI_KEY=your_openai_key  # Required for LLM features"
echo ""
echo "📚 Useful commands:"
echo "   make test          # Run tests"
echo "   make lint          # Run linting"
echo "   python -m pytest tests/test_ai_package.py  # Test AI package"
echo ""
