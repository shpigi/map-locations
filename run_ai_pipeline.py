#!/usr/bin/env python3
"""
Simple wrapper script to run the Map Locations AI pipeline.
This provides an alternative to the CLI command.
"""

import sys
from map_locations_ai.pipeline import main

if __name__ == "__main__":
    sys.exit(main())
