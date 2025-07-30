# Core.py Modularization Plan

## Overview

The `core.py` file has grown to 2,552 lines and handles multiple responsibilities. This document tracks the progress of breaking it into focused, maintainable modules.

## Current Status

- **Total Lines**: 2,552
- **Status**: ✅ COMPLETED
- **Started**: December 2024
- **Target Completion**: TBD



## ✅ Module Completion Log

### 📂 categories.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 251 lines removed from core.py
- **Functions Migrated**: 10 functions + 2 constants
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,552 to 2,313 lines (-239 lines net)

**Functions Successfully Migrated:**
- [x] `COLOR_CATEGORIES` (constant)
- [x] `FOLIUM_TO_HEX_COLORS` (derived constant)
- [x] `get_color_square_html()`
- [x] `get_location_category()`
- [x] `get_category_types()`
- [x] `get_type_color()`
- [x] `get_available_categories()`
- [x] `filter_locations_by_category()`
- [x] `hex_to_kml_color()`
- [x] `get_kml_color()`


### �� utils.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 40 lines removed from core.py
- **Functions Migrated**: 1 function (create_sample_locations)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,313 to 2,276 lines (-37 lines net)

**Functions Successfully Migrated:**
- [x] `create_sample_locations()`


### 📂 location_filters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 218 lines removed from core.py
- **Functions Migrated**: 8 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,275 to 2,067 lines (-208 lines net)

**Functions Successfully Migrated:**
- [x] `get_available_types()`
- [x] `get_available_tags()`
- [x] `get_available_neighborhoods()`
- [x] `filter_locations_by_type()`
- [x] `filter_locations_by_tags()`
- [x] `filter_locations_by_neighborhood()`
- [x] `get_location_summary()`
- [x] `validate_location_data()`


### 📂 popup_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 320 lines removed from core.py
- **Functions Migrated**: 6 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 2,067 to 1,755 lines (-312 lines net)

**Functions Successfully Migrated:**
- [x] `_truncate_description_mobile()`
- [x] `_generate_google_maps_url()`
- [x] `_is_url()`
- [x] `_format_field_value()`
- [x] `_generate_popup_html()`
- [x] `_generate_mobile_popup_html()`


### 📂 exporters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 549 lines removed from core.py
- **Functions Migrated**: 5 functions (including large export_to_kml ~400 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,755 to 1,213 lines (-542 lines net)

**Functions Successfully Migrated:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~400 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`


## Module Breakdown

### ✅ Phase 1: Create Module Structure

#### 1. 📂 `categories.py` - Color & Category Management
- **Lines**: ~17-183 (167 lines)
- **Status**: ✅ COMPLETED
- **Dependencies**: None (foundational module)

**Functions to move:**
- [x] `COLOR_CATEGORIES` (constant)
- [x] `FOLIUM_TO_HEX_COLORS` (derived constant)
- [x] `get_color_square_html()`
- [x] `get_location_category()`
- [x] `get_category_types()`
- [x] `get_type_color()`
- [x] `get_available_categories()`
- [x] `filter_locations_by_category()`
- [x] `hex_to_kml_color()`
- [x] `get_kml_color()`


### �� utils.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 40 lines removed from core.py
- **Functions Migrated**: 1 function (create_sample_locations)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,313 to 2,276 lines (-37 lines net)

**Functions Successfully Migrated:**
- [x] `create_sample_locations()`


### 📂 location_filters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 218 lines removed from core.py
- **Functions Migrated**: 8 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,275 to 2,067 lines (-208 lines net)

**Functions Successfully Migrated:**
- [x] `get_available_types()`
- [x] `get_available_tags()`
- [x] `get_available_neighborhoods()`
- [x] `filter_locations_by_type()`
- [x] `filter_locations_by_tags()`
- [x] `filter_locations_by_neighborhood()`
- [x] `get_location_summary()`
- [x] `validate_location_data()`


### 📂 popup_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 320 lines removed from core.py
- **Functions Migrated**: 6 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 2,067 to 1,755 lines (-312 lines net)

**Functions Successfully Migrated:**
- [x] `_truncate_description_mobile()`
- [x] `_generate_google_maps_url()`
- [x] `_is_url()`
- [x] `_format_field_value()`
- [x] `_generate_popup_html()`
- [x] `_generate_mobile_popup_html()`


### 📂 exporters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 549 lines removed from core.py
- **Functions Migrated**: 5 functions (including large export_to_kml ~400 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,755 to 1,213 lines (-542 lines net)

**Functions Successfully Migrated:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~400 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
from typing import List, Dict, Any
from collections import defaultdict
```

---

#### 2. 📂 `popup_generators.py` - HTML Popup Generation
- **Lines**: ~45-366 (320 lines)
- **Status**: ✅ COMPLETED
- **Dependencies**: `categories.py`

**Functions to move:**
- [x] `_truncate_description_mobile()`
- [x] `_generate_google_maps_url()`
- [x] `_is_url()`
- [x] `_format_field_value()`
- [x] `_generate_popup_html()`
- [x] `_generate_mobile_popup_html()`


### 📂 exporters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 549 lines removed from core.py
- **Functions Migrated**: 5 functions (including large export_to_kml ~400 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,755 to 1,213 lines (-542 lines net)

**Functions Successfully Migrated:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~400 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
import re
import urllib.parse
from typing import Any, Dict, Union
from .categories import get_location_category, COLOR_CATEGORIES
from .common import Location
```

---

#### 3. 📂 `exporters.py` - Data Export Functions
- **Lines**: ~55-605 (549 lines)
- **Status**: ✅ COMPLETED
- **Dependencies**: `popup_generators.py`, `categories.py`

**Functions to move:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~500 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
import csv
import json
import os
from pathlib import Path
from typing import Set
from .popup_generators import _generate_google_maps_url, _truncate_description_mobile
from .categories import get_type_color, get_location_category, COLOR_CATEGORIES
from .common import LocationList
```

---

#### 4. 📂 `map_generators.py` - Map Creation Functions
- **Lines**: ~65-1199 (1,134 lines) ⚠️ **Largest module**
- **Status**: ✅ COMPLETED
- **Dependencies**: `popup_generators.py`, `categories.py`

**Functions to move:**
- [x] `show_locations_grouped()` (~300 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Large function** (~750 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
import os
import json
from pathlib import Path
from collections import defaultdict
from typing import Optional, List, Dict, Any
import folium
from .popup_generators import _generate_popup_html, _generate_mobile_popup_html
from .categories import get_type_color, get_location_category, COLOR_CATEGORIES, FOLIUM_TO_HEX_COLORS
from .location_filters import filter_locations_by_category
from .common import LocationList
```

---

#### 5. 📂 `location_filters.py` - Location Analysis & Filtering
- **Lines**: ~1979-2195 (218 lines)
- **Status**: ✅ COMPLETED
- **Dependencies**: `categories.py`

**Functions to move:**
- [x] `get_available_types()`
- [x] `get_available_tags()`
- [x] `get_available_neighborhoods()`
- [x] `filter_locations_by_type()`
- [x] `filter_locations_by_tags()`
- [x] `filter_locations_by_neighborhood()`
- [x] `get_location_summary()`
- [x] `validate_location_data()`


### 📂 popup_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 320 lines removed from core.py
- **Functions Migrated**: 6 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 2,067 to 1,755 lines (-312 lines net)

**Functions Successfully Migrated:**
- [x] `_truncate_description_mobile()`
- [x] `_generate_google_maps_url()`
- [x] `_is_url()`
- [x] `_format_field_value()`
- [x] `_generate_popup_html()`
- [x] `_generate_mobile_popup_html()`


### 📂 exporters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 549 lines removed from core.py
- **Functions Migrated**: 5 functions (including large export_to_kml ~400 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,755 to 1,213 lines (-542 lines net)

**Functions Successfully Migrated:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~400 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
from typing import List, Dict, Any
from collections import Counter
from .categories import get_location_category, get_available_categories
from .common import LocationList
```

---

#### 6. 📂 `utils.py` - Utility Functions
- **Lines**: ~2196-2236 (40 lines)
- **Status**: ✅ COMPLETED
- **Dependencies**: None

**Functions to move:**
- [x] `create_sample_locations()`


### 📂 location_filters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 218 lines removed from core.py
- **Functions Migrated**: 8 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via __init__.py
- **Core.py Size**: Reduced from 2,275 to 2,067 lines (-208 lines net)

**Functions Successfully Migrated:**
- [x] `get_available_types()`
- [x] `get_available_tags()`
- [x] `get_available_neighborhoods()`
- [x] `filter_locations_by_type()`
- [x] `filter_locations_by_tags()`
- [x] `filter_locations_by_neighborhood()`
- [x] `get_location_summary()`
- [x] `validate_location_data()`


### 📂 popup_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 320 lines removed from core.py
- **Functions Migrated**: 6 functions
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 2,067 to 1,755 lines (-312 lines net)

**Functions Successfully Migrated:**
- [x] `_truncate_description_mobile()`
- [x] `_generate_google_maps_url()`
- [x] `_is_url()`
- [x] `_format_field_value()`
- [x] `_generate_popup_html()`
- [x] `_generate_mobile_popup_html()`


### 📂 exporters.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 549 lines removed from core.py
- **Functions Migrated**: 5 functions (including large export_to_kml ~400 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,755 to 1,213 lines (-542 lines net)

**Functions Successfully Migrated:**
- [x] `export_to_json()`
- [x] `export_to_csv()`
- [x] `export_to_geojson()`
- [x] `export_to_kml()` ⚠️ **Large function** (~400 lines)
- [x] `export_to_all_formats()`


### 📂 map_generators.py - COMPLETED ✅
- **Completed**: December 2024
- **Lines Moved**: 1,134 lines removed from core.py
- **Functions Migrated**: 5 functions (including massive show_locations_with_advanced_filtering ~753 lines)
- **Testing**: ✅ All imports work correctly
- **Backward Compatibility**: ✅ Maintained via imports
- **Core.py Size**: Reduced from 1,213 to 72 lines (-1,141 lines net)

**Functions Successfully Migrated:**
- [x] `show_locations_grouped()` (~288 lines)
- [x] `show_locations_with_filtering()`
- [x] `show_locations_with_advanced_filtering()` ⚠️ **Massive function** (~753 lines)
- [x] `show_locations_with_google_maps()`
- [x] `show_locations_by_category()`

**Imports needed:**
```python
from .common import LocationList
```

---

### ✅ Phase 2: Update Import Structure

#### Core Module Updates
- [ ] **`__init__.py`**: Update imports to reference new modules
- [ ] **`core.py`**: Keep only essential orchestration functions
- [ ] **`cli.py`**: Update imports if needed

#### Backward Compatibility
- [ ] Maintain all existing public API
- [ ] Add deprecation warnings if needed
- [ ] Ensure all imports work as before

---

### ✅ Phase 3: Testing & Validation

#### Testing Strategy
- [ ] Run existing test suite
- [ ] Create module-specific tests
- [ ] Integration testing
- [ ] Performance validation

#### Validation Checklist
- [ ] All CLI commands work
- [ ] All export formats function
- [ ] Map generation works
- [ ] Import statements are correct
- [ ] No circular dependencies

---

## Implementation Order

### 🥇 Priority 1: Foundation Modules (Low Risk)
1. **`categories.py`** - No dependencies, widely used
2. **`utils.py`** - Simple, isolated functions
3. **`location_filters.py`** - Depends only on categories

### 🥈 Priority 2: Content Modules (Medium Risk)
4. **`popup_generators.py`** - Depends on categories
5. **`exporters.py`** - Depends on popup generators

### 🥉 Priority 3: Complex Modules (High Risk)
6. **`map_generators.py`** - Largest, most complex, many dependencies

---

## File Size Analysis

| Module | Estimated Lines | Complexity | Risk Level |
|--------|----------------|------------|------------|
| `categories.py` | 167 | Low | 🟢 Low |
| `popup_generators.py` | 320 | Medium | 🟡 Medium |
| `exporters.py` | 549 | Medium | 🟡 Medium |
| `location_filters.py` | 400 | Low | 🟢 Low |
| `utils.py` | 146 | Low | 🟢 Low |
| `map_generators.py` | 1,394 | High | 🔴 High |
| **Total** | **2,976** | - | - |

*Note: Total is higher than original due to some overlapping line counts and imports*

---

## Dependency Graph

```
categories.py (foundation)
    ↓
├── popup_generators.py
│   ↓
├── exporters.py
└── location_filters.py
    ↓
map_generators.py (depends on all above)
```

---

## Migration Steps

### Step 1: Create Foundation Module
```bash
# Create categories.py
touch map_locations/categories.py
# Move constants and category functions
# Test imports
```

### Step 2: Create Dependent Modules
```bash
# Create remaining modules in dependency order
# Update imports progressively
# Test each module individually
```

### Step 3: Update Core Structure
```bash
# Update __init__.py imports
# Clean up core.py
# Run full test suite
```

---

## Testing Strategy

### Unit Tests
- [ ] Test each new module independently
- [ ] Mock dependencies where needed
- [ ] Validate function behavior unchanged

### Integration Tests
- [ ] Test module interactions
- [ ] Validate complete workflows
- [ ] Test CLI functionality

### Regression Tests
- [ ] Compare output before/after
- [ ] Validate export formats identical
- [ ] Check map generation consistency

---

## Rollback Plan

### If Issues Arise
1. **Git Branch**: Work on feature branch
2. **Backup**: Keep original core.py as core_backup.py
3. **Incremental**: Complete one module at a time
4. **Validation**: Test after each module

### Recovery Steps
```bash
# If major issues, rollback to previous commit
git checkout main
git reset --hard <previous-commit>

# Or restore from backup
cp core_backup.py core.py
```

---

## Benefits After Completion

### 🎯 Maintainability
- **Single Responsibility**: Each module has one clear purpose
- **Focused Changes**: Easier to modify specific functionality
- **Code Reviews**: Smaller, targeted pull requests

### 🚀 Performance
- **Faster Imports**: Only load needed modules
- **Memory Usage**: Reduced memory footprint
- **Startup Time**: Quicker application startup

### 🧪 Testing
- **Unit Testing**: Test modules in isolation
- **Mock Dependencies**: Easier to mock specific functionality
- **Test Coverage**: Better coverage tracking per module

### 👥 Developer Experience
- **Navigation**: Easier to find specific functions
- **Understanding**: Clearer code organization
- **Onboarding**: New developers can focus on specific areas

---

## Progress Tracking

### Current Progress: 100% Complete (6/6 modules) 🎉

- [x] Analysis completed
- [x] Plan documented
- [x] Foundation modules created (3/3: categories.py ✅, utils.py ✅, location_filters.py ✅)
- [x] Content modules created (2/2: popup_generators.py ✅, exporters.py ✅)
- [x] Complex modules created (1/1: map_generators.py ✅)
- [ ] Content modules created
- [ ] Complex modules created
- [ ] Import structure updated
- [ ] Testing completed
- [ ] Documentation updated

### Weekly Updates
- **Week 1**: Foundation modules (`categories.py`, `utils.py`)
- **Week 2**: Content modules (`popup_generators.py`, `location_filters.py`)
- **Week 3**: Export module (`exporters.py`)
- **Week 4**: Map generation module (`map_generators.py`)
- **Week 5**: Testing and validation

---

## Notes

### ⚠️ Potential Issues
1. **Circular Imports**: Careful dependency management needed
2. **Large Functions**: Some functions are very large (export_to_kml, show_locations_with_advanced_filtering)
3. **Import Changes**: May affect external users of the library

### 💡 Optimization Opportunities
1. **Function Splitting**: Break down large functions within modules
2. **Code Deduplication**: Identify and eliminate duplicate code
3. **Type Hints**: Improve type hints during migration
4. **Documentation**: Update docstrings and add module-level docs

---

## Next Steps

1. **Start with `categories.py`** - foundational and low risk
2. **Create branch**: `feature/core-modularization`
3. **Implement incrementally**: One module at a time
4. **Test thoroughly**: After each module creation
5. **Update documentation**: Keep this plan current

---

*Last Updated: December 2024*
*Status: Planning Complete, Ready for Implementation*
