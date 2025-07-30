# Standardized Location Types and Color Mappings

This document outlines the standardized set of location types and their corresponding color mappings used in the Map Locations project. These mappings are designed to provide consistent visual representation across different export formats (Folium maps, KML, etc.) and match Google Maps color conventions.

## Color Scheme Overview

The color scheme follows Google Maps conventions with the following categories:

- **Red**: Food & Drink establishments
- **Light Blue**: Culture & Arts venues
- **Green**: Nature & Outdoors locations
- **Blue**: Shopping & Commerce
- **Light Gray**: Accommodation
- **Gray**: Transport and Urban infrastructure
- **Orange**: Landmarks & Monuments
- **Purple**: Entertainment & Experiences
- **Dark Red**: Neighborhoods & Areas
- **Dark Gray**: Streets & Urban elements

## Complete Type Mappings

### Food & Drink (Red)
```python
"restaurant": "red",
"cafe": "red",
"bar": "red",
"pub": "red",
```

### Culture & Arts (Light Blue)
```python
"museum": "lightblue",
"gallery": "lightblue",
"art gallery": "lightblue",
"theater": "lightblue",
"theatre": "lightblue",
"cinema": "lightblue",
"exhibition": "lightblue",
"studio tour": "lightblue",
```

### Nature & Outdoors (Green)
```python
"park": "green",
"garden": "green",
"botanical garden": "green",
"cemetery": "green",
```

### Shopping & Commerce (Blue)
```python
"shopping": "blue",
"store": "blue",
"market": "blue",
"shopping center": "blue",
"shopping street": "blue",
"passage": "blue",
"covered passage": "blue",
"passage couvert": "blue",
"historic shopping arcades": "blue",
```

### Accommodation (Light Gray)
```python
"hotel": "lightgray",
"accommodation": "lightgray",
"apartment": "lightgray",
```

### Transport (Gray)
```python
"transport": "gray",
"station": "gray",
"metro station": "gray",
```

### Landmarks & Monuments (Orange)
```python
"landmark": "orange",
"monument": "orange",
"church": "orange",
"temple": "orange",
"basilica": "orange",
"palace": "orange",
"bridge": "orange",
```

### Entertainment & Experiences (Purple)
```python
"entertainment": "purple",
"theme park": "purple",
"amusement park": "purple",
"experience": "purple",
```

### Neighborhoods & Areas (Dark Red)
```python
"neighborhood": "darkred",
"district": "darkred",
"theater district": "darkred",
```

### Streets & Urban (Dark Gray)
```python
"street": "darkgray",
```

### Default
```python
"": "gray",  # Empty type
```

## Implementation

These mappings are implemented in two key functions:

1. **`get_type_color(loc_type: str) -> str`**: Returns folium-compatible color names for interactive maps
2. **`export_to_kml()`**: Uses KML-compatible color codes (AABBGGRR format) for Google My Maps export

## Data-Driven Standardization

This standardization is based on analysis of actual location data from:

- **London Dataset**: 49 deduplicated locations with 14 unique types
- **Paris Dataset**: 77 deduplicated locations with 26 unique types

### Common Types Found in Both Datasets
- `hotel`, `landmark`, `market`, `museum`, `neighborhood`, `park`, `theater`

### London-Specific Types
- `district`, `gallery`, `shopping center`, `shopping street`, `street`, `studio tour`, `theater district`

### Paris-Specific Types
- `amusement park`, `apartment`, `art gallery`, `basilica`, `botanical garden`, `cafe`, `cemetery`, `covered passage`, `exhibition`, `metro station`, `palace`, `passage`, `passage couvert`, `shopping center`, `transport`

## Usage Guidelines

1. **Consistency**: Always use the standardized type names when adding new locations
2. **Case Insensitive**: The system handles type matching case-insensitively
3. **Fallback**: Unknown types default to gray color
4. **Extensibility**: New types can be added to the color mappings as needed

## Future Considerations

- Consider adding subcategories for more granular classification
- Implement type validation to ensure consistency
- Add support for custom color schemes
- Consider seasonal or thematic color variations
