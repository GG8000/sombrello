# tests/test_raycasting.py

from datetime import datetime, timezone
from unittest.mock import patch

import geopandas as gpd
from shapely.geometry import Polygon
import pytest

from sombrello.shadow.raycasting import shadow_index
from sombrello.solar.solar import SolarPosition
from sombrello.models.trackpoint import Trackpoint


@pytest.fixture
def fake_building_gpkg(tmp_path):
    """
    A single 20m-tall building, roughly 20x20m, centered near
    lat=48.1375, lon=11.5755.
    """
    square = Polygon([
        (11.5749, 48.1374), (11.5751, 48.1374),
        (11.5751, 48.1376), (11.5749, 48.1376),
    ])
    gdf = gpd.GeoDataFrame({"height": [20.0]}, geometry=[square], crs="EPSG:4326")
    path = tmp_path / "test_buildings.gpkg"
    gdf.to_file(path, driver="GPKG")
    return str(path)


@pytest.fixture
def empty_trees_gpkg(tmp_path):
    """No trees — isolates the test to building shadow only."""
    gdf = gpd.GeoDataFrame({"height": []}, geometry=[], crs="EPSG:4326")
    path = tmp_path / "empty_trees.gpkg"
    gdf.to_file(path, driver="GPKG")
    return str(path)


def _make_trackpoint(lat, lon):
    return Trackpoint(
        lat=lat,
        lon=lon,
        elevation_m=0.0,
        timestamp=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
    )


@patch("sombrello.shadow.raycasting.sun_position")
def test_point_in_shadow_direction_is_shadowed(mock_sun, fake_building_gpkg, empty_trees_gpkg):
    mock_sun.return_value = SolarPosition(azimuth_deg=90.0, elevation_deg=10.0)

    # was: lon=11.5730  (222.6m away — outside the 113.4m shadow)
    tp = _make_trackpoint(lat=48.1375, lon=11.57428)  # updated, ~80m away

    result = shadow_index(tp, buildings_path=fake_building_gpkg, trees_path=empty_trees_gpkg)
    assert result == 1.0


@patch("sombrello.shadow.raycasting.sun_position")
def test_point_opposite_shadow_direction_is_lit(mock_sun, fake_building_gpkg, empty_trees_gpkg):
    # Same sun position as above.
    mock_sun.return_value = SolarPosition(azimuth_deg=90.0, elevation_deg=10.0)

    # Point placed east of the building — shadow falls the opposite way, so this stays lit.
    tp = _make_trackpoint(lat=48.1375, lon=11.5770)

    result = shadow_index(tp, buildings_path=fake_building_gpkg, trees_path=empty_trees_gpkg)
    assert result == 0.0


@patch("sombrello.shadow.raycasting.sun_position")
def test_sun_below_horizon_is_fully_shadowed(mock_sun, fake_building_gpkg, empty_trees_gpkg):
    mock_sun.return_value = SolarPosition(azimuth_deg=90.0, elevation_deg=-5.0)

    tp = _make_trackpoint(lat=48.1375, lon=11.5755)  # location doesn't matter here

    result = shadow_index(tp, buildings_path=fake_building_gpkg, trees_path=empty_trees_gpkg)
    assert result == 1.0