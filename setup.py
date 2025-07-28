#!/usr/bin/env python3
"""
Setup script for Map Locations AI
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="map-locations-ai",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered location extraction and mapping tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/map-locations-ai",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai>=1.0.0",
        "pyyaml>=6.0",
        "folium>=0.14.0",
        "requests>=2.28.0",
        "beautifulsoup4>=4.11.0",
        "simplekml>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "isort>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "map-locations-ai=map_locations_ai.pipeline:main",
        ],
    },
)
