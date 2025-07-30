"""
Tests for core functionality of map_locations package.
"""

import os
import tempfile
from typing import Any, Dict, List, cast
from unittest.mock import mock_open, patch
from urllib.error import URLError
from urllib.request import urlopen

import pytest

from map_locations.core import (
    Location,
    create_sample_locations,
    export_to_all_formats,
    export_to_csv,
    export_to_geojson,
    export_to_json,
    export_to_kml,
    filter_locations_by_neighborhood,
    filter_locations_by_tags,
    filter_locations_by_type,
    get_available_neighborhoods,
    get_available_tags,
    get_available_types,
    get_kml_color,
    get_location_summary,
    load_locations_from_yaml,
    validate_location_data,
)


class TestLoadLocationsFromYaml:
    """Test loading locations from YAML files."""

    def test_load_locations_valid_yaml(self) -> None:
        """Test loading locations from valid YAML."""
        yaml_content = """
        locations:
          - name: "Test Location"
            type: "restaurant"
            latitude: 40.7128
            longitude: -74.0060
            tags: ["food", "dinner"]
            neighborhood: "Manhattan"
            date_added: "2024-01-01"
        """

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=yaml_content)),
        ):
            locations = load_locations_from_yaml("dummy.yaml")

        assert len(locations) == 1
        assert locations[0]["name"] == "Test Location"
        assert locations[0]["type"] == "restaurant"
        assert locations[0]["latitude"] == 40.7128
        assert locations[0]["longitude"] == -74.0060
        assert locations[0]["tags"] == ["food", "dinner"]
        assert locations[0]["neighborhood"] == "Manhattan"
        assert locations[0]["date_added"] == "2024-01-01"

    def test_load_locations_empty_yaml(self) -> None:
        """Test loading from YAML with no locations."""
        yaml_content = "locations: []"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=yaml_content)),
        ):
            locations = load_locations_from_yaml("dummy.yaml")

        assert locations == []

    def test_load_locations_missing_locations_key(self) -> None:
        """Test loading from YAML without locations key."""
        yaml_content = "other_key: value"

        with (
            patch("os.path.exists", return_value=True),
            patch("builtins.open", mock_open(read_data=yaml_content)),
        ):
            locations = load_locations_from_yaml("dummy.yaml")

        assert locations == []


class TestAIUtilityFunctions:
    """Test AI-friendly utility functions."""

    @pytest.fixture  # type: ignore[misc]
    def sample_locations(self) -> List[Location]:
        """Sample location data for testing."""
        return cast(
            List[Location],
            [
                {
                    "name": "Test Location 1",
                    "type": "restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "tags": ["food", "dinner"],
                    "neighborhood": "Manhattan",
                    "date_added": "2024-01-01",
                },
                {
                    "name": "Test Location 2",
                    "type": "cafe",
                    "latitude": 40.7589,
                    "longitude": -73.9851,
                    "tags": ["coffee", "breakfast"],
                    "neighborhood": "Midtown",
                    "date_added": "2024-01-02",
                },
                {
                    "name": "Test Location 3",
                    "type": "restaurant",
                    "latitude": 40.7505,
                    "longitude": -73.9934,
                    "tags": ["food", "lunch"],
                    "neighborhood": "Manhattan",
                    "date_added": "2024-01-03",
                },
            ],
        )

    def test_get_available_types(self, sample_locations: List[Location]) -> None:
        """Test getting available location types."""
        types = get_available_types(sample_locations)
        assert set(types) == {"restaurant", "cafe"}
        assert len(types) == 2

    def test_get_available_tags(self, sample_locations: List[Location]) -> None:
        """Test getting available tags."""
        tags = get_available_tags(sample_locations)
        expected_tags = {"food", "dinner", "coffee", "breakfast", "lunch"}
        assert set(tags) == expected_tags
        assert len(tags) == 5

    def test_get_available_neighborhoods(
        self, sample_locations: List[Location]
    ) -> None:
        """Test getting available neighborhoods."""
        neighborhoods = get_available_neighborhoods(sample_locations)
        assert set(neighborhoods) == {"Manhattan", "Midtown"}
        assert len(neighborhoods) == 2

    def test_filter_locations_by_type(self, sample_locations: List[Location]) -> None:
        """Test filtering locations by type."""
        restaurants = filter_locations_by_type(sample_locations, ["restaurant"])
        assert len(restaurants) == 2
        assert all(loc["type"] == "restaurant" for loc in restaurants)

        cafes = filter_locations_by_type(sample_locations, ["cafe"])
        assert len(cafes) == 1
        assert all(loc["type"] == "cafe" for loc in cafes)

        food_locations = filter_locations_by_type(
            sample_locations, ["restaurant", "cafe"]
        )
        assert len(food_locations) == 3

    def test_filter_locations_by_tags(self, sample_locations: List[Location]) -> None:
        """Test filtering locations by tags."""
        food_locations = filter_locations_by_tags(sample_locations, ["food"])
        assert len(food_locations) == 2
        assert all("food" in loc["tags"] for loc in food_locations)

        coffee_locations = filter_locations_by_tags(sample_locations, ["coffee"])
        assert len(coffee_locations) == 1
        assert all("coffee" in loc["tags"] for loc in coffee_locations)

        multiple_tags = filter_locations_by_tags(sample_locations, ["food", "coffee"])
        assert len(multiple_tags) == 3

    def test_filter_locations_by_neighborhood(
        self, sample_locations: List[Location]
    ) -> None:
        """Test filtering locations by neighborhood."""
        manhattan_locations = filter_locations_by_neighborhood(
            sample_locations, ["Manhattan"]
        )
        assert len(manhattan_locations) == 2
        assert all(loc["neighborhood"] == "Manhattan" for loc in manhattan_locations)

        midtown_locations = filter_locations_by_neighborhood(
            sample_locations, ["Midtown"]
        )
        assert len(midtown_locations) == 1
        assert all(loc["neighborhood"] == "Midtown" for loc in midtown_locations)

    def test_get_location_summary(self, sample_locations: List[Location]) -> None:
        """Test getting location summary."""
        summary = get_location_summary(sample_locations)

        assert summary["total_count"] == 3
        assert set(summary["types"]) == {"restaurant", "cafe"}
        assert set(summary["tags"]) == {
            "food",
            "dinner",
            "coffee",
            "breakfast",
            "lunch",
        }
        assert set(summary["neighborhoods"]) == {"Manhattan", "Midtown"}
        assert summary["type_counts"]["restaurant"] == 2
        assert summary["type_counts"]["cafe"] == 1
        assert summary["neighborhood_counts"]["Manhattan"] == 2
        assert summary["neighborhood_counts"]["Midtown"] == 1

    def test_validate_location_data_valid(
        self, sample_locations: List[Location]
    ) -> None:
        """Test validation with valid data."""
        issues = validate_location_data(sample_locations)
        assert not any(issues.values())

    def test_validate_location_data_missing_required(self) -> None:
        """Test validation with missing required fields."""
        invalid_locations = cast(
            List[Location],
            [
                {
                    "name": "Test Location",
                    "type": "restaurant",
                    # Missing latitude and longitude
                },
                {
                    "name": "Test Location 2",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    # Missing type
                },
            ],
        )

        issues = validate_location_data(invalid_locations)
        assert (
            len(issues["missing_required"]) == 3
        )  # 2 missing lat/lon + 1 missing type

    def test_validate_location_data_invalid_coordinates(self) -> None:
        """Test validation with invalid coordinates."""
        invalid_locations = cast(
            List[Location],
            [
                {
                    "name": "Test Location",
                    "type": "restaurant",
                    "latitude": 100.0,  # Invalid latitude
                    "longitude": -74.0060,
                },
                {
                    "name": "Test Location 2",
                    "type": "cafe",
                    "latitude": 40.7128,
                    "longitude": 200.0,  # Invalid longitude
                },
            ],
        )

        issues = validate_location_data(invalid_locations)
        assert len(issues["invalid_coordinates"]) == 2

    def test_create_sample_locations(self) -> None:
        """Test creating sample locations."""
        sample_locations = create_sample_locations()

        assert len(sample_locations) == 3
        assert sample_locations[0]["name"] == "Eiffel Tower"
        assert sample_locations[0]["type"] == "landmark"
        assert sample_locations[1]["name"] == "Louvre Museum"
        assert sample_locations[1]["type"] == "museum"
        assert sample_locations[2]["name"] == "Notre-Dame Cathedral"
        assert sample_locations[2]["type"] == "church"

        # Check that all required fields are present
        for location in sample_locations:
            assert "name" in location
            assert "type" in location
            assert "latitude" in location
            assert "longitude" in location
            assert isinstance(location["latitude"], (int, float))
            assert isinstance(location["longitude"], (int, float))


class TestExportFunctions:
    """Test export functions."""

    @pytest.fixture  # type: ignore[misc]
    def sample_locations(self) -> List[Location]:
        """Sample location data for testing."""
        return cast(
            List[Location],
            [
                {
                    "name": "Test Location 1",
                    "type": "restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "tags": ["food", "dinner"],
                    "neighborhood": "Manhattan",
                    "date_added": "2024-01-01",
                },
                {
                    "name": "Test Location 2",
                    "type": "cafe",
                    "latitude": 40.7589,
                    "longitude": -73.9851,
                    "tags": ["coffee", "breakfast"],
                    "neighborhood": "Midtown",
                    "date_added": "2024-01-02",
                },
            ],
        )

    def test_export_to_json(self, sample_locations: List[Location]) -> None:
        """Test JSON export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            export_to_json(sample_locations, temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content
            with open(temp_path, "r") as f:
                content = f.read()
                assert "Test Location 1" in content
                assert "Test Location 2" in content
                assert "restaurant" in content
                assert "cafe" in content
        finally:
            os.unlink(temp_path)

    def test_export_to_csv(self, sample_locations: List[Location]) -> None:
        """Test CSV export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            export_to_csv(sample_locations, temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content
            with open(temp_path, "r") as f:
                content = f.read()
                assert "Test Location 1" in content
                assert "Test Location 2" in content
                assert "restaurant" in content
                assert "cafe" in content
                assert "food, dinner" in content
        finally:
            os.unlink(temp_path)

    def test_export_to_geojson(self, sample_locations: List[Location]) -> None:
        """Test GeoJSON export."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".geojson", delete=False
        ) as f:
            temp_path = f.name

        try:
            export_to_geojson(sample_locations, temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content
            with open(temp_path, "r") as f:
                content = f.read()
                assert "FeatureCollection" in content
                assert "Test Location 1" in content
                assert "Test Location 2" in content
                assert "Point" in content
                assert "40.7128" in content
                # JSON doesn't preserve trailing zeros
                assert "-74.006" in content
        finally:
            os.unlink(temp_path)

    def test_export_to_kml(self, sample_locations: List[Location]) -> None:
        """Test KML export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            export_to_kml(sample_locations, temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content
            with open(temp_path, "r") as f:
                content = f.read()
                assert "<?xml" in content
                assert "<kml" in content
                assert "Test Location 1" in content
                assert "Test Location 2" in content
                assert "restaurant" in content
                assert "cafe" in content
        finally:
            os.unlink(temp_path)

    def test_export_to_all_formats(self, sample_locations: List[Location]) -> None:
        """Test export to all formats."""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "test_export")

            export_to_all_formats(sample_locations, base_path)

            # Check all files were created
            expected_files = [
                f"{base_path}.json",
                f"{base_path}.csv",
                f"{base_path}.geojson",
                f"{base_path}.kml",
            ]

            for file_path in expected_files:
                assert os.path.exists(file_path), f"File {file_path} was not created"


class TestMapGeneration:
    """Test map generation functions."""

    @pytest.fixture  # type: ignore[misc]
    def sample_locations(self) -> List[Location]:
        """Sample location data for testing."""
        return cast(
            List[Location],
            [
                {
                    "name": "Test Location 1",
                    "type": "restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                    "tags": ["food", "dinner"],
                    "neighborhood": "Manhattan",
                    "date_added": "2024-01-01",
                },
                {
                    "name": "Test Location 2",
                    "type": "cafe",
                    "latitude": 40.7589,
                    "longitude": -73.9851,
                    "tags": ["coffee", "breakfast"],
                    "neighborhood": "Midtown",
                    "date_added": "2024-01-02",
                },
            ],
        )

    def test_show_locations_grouped_creates_file(
        self, sample_locations: List[Location]
    ) -> None:
        """Test that show_locations_grouped creates an HTML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            from map_locations.core import show_locations_grouped

            show_locations_grouped(sample_locations, map_filename=temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content
            with open(temp_path, "r") as f:
                content = f.read()
                assert "<!DOCTYPE html>" in content
                assert "folium" in content
                assert "Test Location 1" in content
                assert "Test Location 2" in content
        finally:
            os.unlink(temp_path)

    def test_show_locations_grouped_empty_locations(self) -> None:
        """Test show_locations_grouped with empty locations list."""
        from map_locations.core import show_locations_grouped

        # Should raise ValueError when no locations provided
        with pytest.raises(ValueError, match="No locations provided."):
            show_locations_grouped([], map_filename="test_empty.html")


class TestKMLIconURLs:
    """Test KML icon URL accessibility."""

    def test_kml_icon_urls_are_accessible(self) -> None:
        """Test that KML icon URLs are accessible."""
        from map_locations.core import export_to_kml

        sample_locations = cast(
            List[Location],
            [
                {
                    "name": "Test Location",
                    "type": "restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                }
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            export_to_kml(sample_locations, temp_path)

            # Check that the KML file contains valid icon URLs
            with open(temp_path, "r") as f:
                content = f.read()
                assert (
                    "https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
                    in content
                )

            # Test that icon URLs are accessible (optional test)
            try:
                # This might fail in some environments, so we make it optional
                response = urlopen(
                    "https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
                )
                assert response.getcode() == 200
            except URLError:
                # If the URL is not accessible, that's okay for testing
                pass

        finally:
            os.unlink(temp_path)

    def test_kml_export_uses_valid_icons(self) -> None:
        """Test that KML export uses valid icon references."""
        from map_locations.core import export_to_kml

        sample_locations = cast(
            List[Location],
            [
                {
                    "name": "Test Restaurant",
                    "type": "restaurant",
                    "latitude": 40.7128,
                    "longitude": -74.0060,
                },
                {
                    "name": "Test Museum",
                    "type": "museum",
                    "latitude": 40.7589,
                    "longitude": -73.9851,
                },
            ],
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            export_to_kml(sample_locations, temp_path)

            with open(temp_path, "r") as f:
                content = f.read()
                # Check that the modern Google Static Maps icon is used
                assert (
                    "https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
                    in content
                )
                # Check that different colors are used for different types
                # Use core functions to get expected colors
                restaurant_color = get_kml_color("restaurant")
                museum_color = get_kml_color("museum")
                assert restaurant_color in content
                assert museum_color in content

        finally:
            os.unlink(temp_path)
