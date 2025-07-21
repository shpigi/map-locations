# Data Format

Complete guide to the YAML data format used by Map Locations.

## Table of Contents

- [Overview](#overview)
- [Required Fields](#required-fields)
- [Optional Fields](#optional-fields)
- [Examples](#examples)
- [Validation Rules](#validation-rules)
- [Best Practices](#best-practices)

## Overview

Map Locations uses YAML format for storing location data. The file should contain a `locations` key with a list of location objects.

## Required Fields

### `name` (string)
The name of the location.

**Examples:**
- `"Eiffel Tower"`
- `"Central Park"`
- `"Galerie Vivienne"`

### `type` (string)
The category or type of location. This determines the color on the map.

**Common Types:**
- `"landmark"`
- `"restaurant"`
- `"cafe"`
- `"museum"`
- `"park"`
- `"passage"`
- `"hotel"`
- `"shop"`

### `latitude` (float)
Latitude coordinate in decimal degrees.

**Range:** -90 to 90

**Examples:**
- `48.8584` (Eiffel Tower)
- `40.7829` (Central Park)
- `48.8667` (Galerie Vivienne)

### `longitude` (float)
Longitude coordinate in decimal degrees.

**Range:** -180 to 180

**Examples:**
- `2.2945` (Eiffel Tower)
- `-73.9654` (Central Park)
- `2.3397` (Galerie Vivienne)

## Optional Fields

### `tags` (list of strings)
Tags for filtering and categorization.

**Examples:**
```yaml
tags: ["historic", "tourist", "architecture"]
tags: ["outdoor", "recreation", "nature"]
tags: ["food", "local", "authentic"]
```

### `neighborhood` (string)
The neighborhood or area where the location is situated.

**Examples:**
- `"7th arrondissement"`
- `"Upper East Side"`
- `"Downtown"`
- `"City Center"`

### `date_added` (string)
Date when the location was added to the collection.

**Format:** YYYY-MM-DD

**Examples:**
- `"2025-01-15"`
- `"2024-12-20"`

### `date_of_visit` (string)
Date when you visited the location.

**Format:** YYYY-MM-DD

**Examples:**
- `"2025-01-20"`
- `"2024-12-25"`

## Examples

### Basic Location

```yaml
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
```

### Complete Location

```yaml
locations:
  - name: "Galerie Vivienne"
    type: "passage"
    latitude: 48.8667
    longitude: 2.3397
    tags: ["historic", "architecture", "glass roof"]
    neighborhood: "2nd arrondissement"
    date_added: "2025-01-15"
    date_of_visit: "2025-01-20"
```

### Multiple Locations

```yaml
locations:
  - name: "Central Park"
    type: "park"
    latitude: 40.7829
    longitude: -73.9654
    tags: ["outdoor", "recreation", "nature"]
    neighborhood: "Upper East Side"
    date_added: "2025-01-10"
    date_of_visit: "2025-01-25"

  - name: "Times Square"
    type: "landmark"
    latitude: 40.758
    longitude: -73.9855
    tags: ["tourist", "entertainment", "shopping"]
    neighborhood: "Midtown"
    date_added: "2025-01-10"
    date_of_visit: "2025-01-26"

  - name: "Brooklyn Bridge"
    type: "bridge"
    latitude: 40.7061
    longitude: -73.9969
    tags: ["landmark", "architecture", "views"]
    neighborhood: "Brooklyn"
    date_added: "2025-01-10"
    date_of_visit: "2025-01-27"
```

## Validation Rules

### Coordinate Validation

- **Latitude**: Must be between -90 and 90
- **Longitude**: Must be between -180 and 180
- **Format**: Decimal degrees (not degrees/minutes/seconds)

### Date Validation

- **Format**: YYYY-MM-DD
- **Examples**: `"2025-01-15"`, `"2024-12-20"`
- **Invalid**: `"15/01/2025"`, `"2025-1-15"`

### Name Validation

- **Required**: Cannot be empty
- **Unique**: Should be unique within the dataset
- **Length**: Reasonable length (1-100 characters)

### Type Validation

- **Required**: Cannot be empty
- **Case**: Case-sensitive
- **Examples**: `"landmark"`, `"restaurant"`, `"museum"`

## Best Practices

### 1. Use Descriptive Names

```yaml
# Good
- name: "Eiffel Tower"
- name: "Central Park"

# Avoid
- name: "Tower"
- name: "Park"
```

### 2. Use Consistent Types

```yaml
# Good - consistent naming
- type: "restaurant"
- type: "cafe"
- type: "bar"

# Avoid - inconsistent
- type: "restaurant"
- type: "Restaurant"
- type: "RESTAURANT"
```

### 3. Use Meaningful Tags

```yaml
# Good - specific and useful
tags: ["historic", "architecture", "glass roof"]
tags: ["outdoor", "recreation", "nature"]

# Avoid - too generic
tags: ["place"]
tags: ["thing"]
```

### 4. Use Proper Date Format

```yaml
# Good
date_added: "2025-01-15"
date_of_visit: "2025-01-20"

# Avoid
date_added: "15/01/2025"
date_of_visit: "2025-1-20"
```

### 5. Use Consistent Neighborhood Names

```yaml
# Good - consistent naming
neighborhood: "Upper East Side"
neighborhood: "Midtown"

# Avoid - inconsistent
neighborhood: "Upper East Side"
neighborhood: "upper east side"
neighborhood: "UES"
```

### 6. Group Related Locations

```yaml
# Good - logical grouping
locations:
  # Paris landmarks
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945

  - name: "Arc de Triomphe"
    type: "landmark"
    latitude: 48.8738
    longitude: 2.2950

  # Paris restaurants
  - name: "Le Comptoir du Relais"
    type: "restaurant"
    latitude: 48.8667
    longitude: 2.3397
```

## Common Issues

### 1. Missing Required Fields

```yaml
# ❌ Missing required fields
locations:
  - name: "Eiffel Tower"
    # Missing: type, latitude, longitude

# ✅ Complete location
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
```

### 2. Invalid Coordinates

```yaml
# ❌ Invalid coordinates
locations:
  - name: "Invalid Place"
    type: "landmark"
    latitude: 91.0  # Should be -90 to 90
    longitude: 181.0  # Should be -180 to 180

# ✅ Valid coordinates
locations:
  - name: "Valid Place"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
```

### 3. Invalid Date Format

```yaml
# ❌ Invalid date format
locations:
  - name: "Old Place"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
    date_added: "15/01/2025"  # Should be YYYY-MM-DD

# ✅ Valid date format
locations:
  - name: "New Place"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
    date_added: "2025-01-15"
```

### 4. Duplicate Names

```yaml
# ❌ Duplicate names
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945

  - name: "Eiffel Tower"  # Duplicate name
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945

# ✅ Unique names
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945

  - name: "Arc de Triomphe"  # Different name
    type: "landmark"
    latitude: 48.8738
    longitude: 2.2950
```

## File Structure

### Complete Example File

```yaml
# my_locations.yaml
locations:
  - name: "Eiffel Tower"
    type: "landmark"
    latitude: 48.8584
    longitude: 2.2945
    tags: ["historic", "tourist", "architecture"]
    neighborhood: "7th arrondissement"
    date_added: "2025-01-15"
    date_of_visit: "2025-01-20"

  - name: "Louvre Museum"
    type: "museum"
    latitude: 48.8606
    longitude: 2.3376
    tags: ["art", "historic", "culture"]
    neighborhood: "1st arrondissement"
    date_added: "2025-01-15"
    date_of_visit: "2025-01-21"

  - name: "Le Comptoir du Relais"
    type: "restaurant"
    latitude: 48.8667
    longitude: 2.3397
    tags: ["food", "local", "authentic"]
    neighborhood: "6th arrondissement"
    date_added: "2025-01-15"
    date_of_visit: "2025-01-22"
```
