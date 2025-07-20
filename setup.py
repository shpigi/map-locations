#!/usr/bin/env python3
"""
Setup script for map_locations package.
"""

import os
from typing import List

from setuptools import find_packages, setup


# Read the README file for long description
def read_readme() -> str:
    """Read README.md file for long description."""
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


# Read requirements from requirements.txt if it exists
def read_requirements() -> List[str]:
    """Read requirements from requirements.txt file."""
    requirements_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(requirements_path):
        with open(requirements_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


setup(
    name="map-locations",
    version="0.1.0",
    author="Lavi Shpigelman",
    author_email="shpigi+map_locations@gmail.com",
    description=(
        "A Python library and CLI tool for mapping locations with interactive "
        "filtering and visualization capabilities"
    ),
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/shpigi/map-locations",
    project_urls={
        "Bug Reports": "https://github.com/shpigi/map-locations/issues",
        "Source": "https://github.com/shpigi/map-locations",
        "Documentation": "https://github.com/shpigi/map-locations#readme",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.10",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
            "twine>=4.0.0",
            "build>=1.0.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "map-locations=map_locations.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords="maps, locations, gis, folium, yaml, geojson, kml",
    license="MIT",
)
