"""
AI Agent for automatic location data curation and enrichment.

This package provides tools to automatically extract, validate, and enrich
location data from various sources including text, URLs, and web content.

Main Components:
- Pipeline: Main processing pipeline for location data
- Extractors: Extract location information from text and URLs
- Enrichers: Gather additional data from external sources
- Validators: Validate and score location data accuracy
- Interfaces: CLI and web interfaces for user interaction
"""

from .agent.pipeline import LocationPipeline
from .interfaces.cli import main as cli_main

__version__ = "0.1.0"
__all__ = ["LocationPipeline", "cli_main"]
