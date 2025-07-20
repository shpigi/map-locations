"""
Tests for core functionality of map_locations package.
"""

import os
import tempfile
from typing import Any, Dict, List
from unittest.mock import mock_open, patch
from urllib.error import URLError
from urllib.request import urlopen

import pytest

from map_locations.core import (
    export_to_all_formats,
    export_to_csv,
    export_to_geojson,
    export_to_json,
    export_to_kml,
    load_locations_from_yaml,
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

        with patch("builtins.open", mock_open(read_data=yaml_content)):
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

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            locations = load_locations_from_yaml("dummy.yaml")

        assert locations == []

    def test_load_locations_missing_locations_key(self) -> None:
        """Test loading from YAML without locations key."""
        yaml_content = "other_key: value"

        with patch("builtins.open", mock_open(read_data=yaml_content)):
            locations = load_locations_from_yaml("dummy.yaml")

        assert locations == []


class TestExportFunctions:
    """Test export functions."""

    @pytest.fixture  # type: ignore[misc]
    def sample_locations(self) -> List[Dict[str, Any]]:
        """Sample location data for testing."""
        return [
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
        ]

    def test_export_to_json(self, sample_locations: List[Dict[str, Any]]) -> None:
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

    def test_export_to_csv(self, sample_locations: List[Dict[str, Any]]) -> None:
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

    def test_export_to_geojson(self, sample_locations: List[Dict[str, Any]]) -> None:
        """Test GeoJSON export."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".geojson", delete=False) as f:
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

    def test_export_to_kml(self, sample_locations: List[Dict[str, Any]]) -> None:
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

    def test_export_to_all_formats(self, sample_locations: List[Dict[str, Any]]) -> None:
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
    """Test map generation functionality."""

    @pytest.fixture  # type: ignore[misc]
    def sample_locations(self) -> List[Dict[str, Any]]:
        """Sample location data for testing."""
        return [
            {
                "name": "Test Location 1",
                "type": "restaurant",
                "latitude": 40.7128,
                "longitude": -74.0060,
                "tags": ["food", "dinner"],
                "neighborhood": "Manhattan",
                "date_added": "2024-01-01",
            },
        ]

    def test_show_locations_grouped_creates_file(
        self, sample_locations: List[Dict[str, Any]]
    ) -> None:
        """Test that map generation creates an HTML file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as f:
            temp_path = f.name

        try:
            from map_locations.core import show_locations_grouped

            show_locations_grouped(sample_locations, map_filename=temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check it's an HTML file
            with open(temp_path, "r") as f:
                content = f.read()
                assert "<!DOCTYPE html>" in content
                assert "folium" in content.lower()
        finally:
            os.unlink(temp_path)

    def test_show_locations_grouped_empty_locations(self) -> None:
        """Test map generation with empty locations list."""
        from map_locations.core import show_locations_grouped

        with pytest.raises(ValueError, match="No locations provided"):
            show_locations_grouped([], map_filename="dummy.html")


class TestKMLIconURLs:
    """Test that KML icon URLs are accessible."""

    def test_kml_icon_urls_are_accessible(self) -> None:
        """Test that all Google Maps KML icon URLs are accessible."""
        # Define the icon URLs used in the KML export
        icon_urls = [
            "http://maps.google.com/mapfiles/kml/paddle/red-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/ltblu-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/grn-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/blu-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/ylw-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/wht-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/orange-circle.png",
            "http://maps.google.com/mapfiles/kml/paddle/purple-circle.png",
        ]

        failed_urls = []

        for url in icon_urls:
            try:
                with urlopen(url) as response:
                    # Check that the response is successful (HTTP 200)
                    assert (
                        response.getcode() == 200
                    ), f"URL {url} returned status code {response.getcode()}"
                    # Check that it's actually an image
                    content_type = response.headers.get("Content-Type", "")
                    assert (
                        "image" in content_type.lower()
                    ), f"URL {url} returned content type {content_type}, expected image"
            except URLError as e:
                failed_urls.append(f"{url}: {e}")
            except Exception as e:
                failed_urls.append(f"{url}: {e}")

        # If any URLs failed, raise an assertion error with details
        if failed_urls:
            raise AssertionError(
                f"The following KML icon URLs are not accessible:\n" f"{chr(10).join(failed_urls)}"
            )

    def test_kml_export_uses_valid_icons(self) -> None:
        """Test that KML export generates content with valid icon references."""
        sample_locations = [
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
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".kml", delete=False) as f:
            temp_path = f.name

        try:
            export_to_kml(sample_locations, temp_path)

            # Check file was created
            assert os.path.exists(temp_path)

            # Check content contains valid icon references
            with open(temp_path, "r") as f:
                content = f.read()

                # Check that the content contains icon references
                assert "paddle/" in content
                assert "circle.png" in content

                # Check for specific icon types we expect
                assert "red-circle.png" in content  # restaurant
                assert "ltblu-circle.png" in content  # museum

                # Verify the URLs are properly formatted
                assert "http://maps.google.com/mapfiles/kml/paddle/" in content
        finally:
            os.unlink(temp_path)
