import csv
import json
import os
import re
import urllib.parse
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union, cast

import folium
import yaml

# Import from categories module
from .categories import (
    COLOR_CATEGORIES,
    FOLIUM_TO_HEX_COLORS,
    filter_locations_by_category,
    get_available_categories,
    get_category_types,
    get_color_square_html,
    get_kml_color,
    get_location_category,
    get_type_color,
    hex_to_kml_color,
)

# Import common models
from .common import Location, LocationList, load_locations_from_yaml

# Import from exporters module
from .exporters import (
    export_to_all_formats,
    export_to_csv,
    export_to_geojson,
    export_to_json,
    export_to_kml,
)

# Import from location_filters module
from .location_filters import (
    filter_locations_by_neighborhood,
    filter_locations_by_tags,
    filter_locations_by_type,
    get_available_neighborhoods,
    get_available_tags,
    get_available_types,
    get_location_summary,
    validate_location_data,
)

# Import from map_generators module
from .map_generators import (
    show_locations_by_category,
    show_locations_grouped,
    show_locations_with_filtering,
    show_locations_with_google_maps,
)

# Import from popup_generators module
from .popup_generators import (
    _format_field_value,
    _generate_google_maps_url,
    _generate_mobile_popup_html,
    _generate_popup_html,
    _is_url,
    _truncate_description_mobile,
)

# Import from utils module
from .utils import create_sample_locations
