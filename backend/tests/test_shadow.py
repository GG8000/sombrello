import pytest
from datetime import datetime, timezone

import geopandas as gpd

from sombrello.solar.solar import sun_position
from sombrello.shadow import shadow_index, shadow_index_many
from sombrello.models.trackpoint import Trackpoint


@pytest.fixture
def empty_buildings_gpkg(tmp_path):
    """No buildings — isolates tests from needing real obstruction data."""
    gdf = gpd.GeoDataFrame({"height": []}, geometry=[], crs="EPSG:4326")
    path = tmp_path / "empty_buildings.gpkg"
    gdf.to_file(path, driver="GPKG")
    return str(path)


@pytest.fixture
def empty_trees_gpkg(tmp_path):
    gdf = gpd.GeoDataFrame({"height": []}, geometry=[], crs="EPSG:4326")
    path = tmp_path / "empty_trees.gpkg"
    gdf.to_file(path, driver="GPKG")
    return str(path)


@pytest.fixture
def tp() -> Trackpoint:
    lat = 49.9
    lon = 10.6
    elevation_m = 1300.0
    timestamp = datetime(2024, 6, 21, 12, tzinfo=timezone.utc)
    return Trackpoint(lat=lat, lon=lon, elevation_m=elevation_m, timestamp=timestamp)


def test_shadow_index_is_a_fraction(tp, empty_buildings_gpkg, empty_trees_gpkg):
    result = shadow_index(tp, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg)
    assert result >= 0.0
    assert result <= 1.0


def test_shadow_index_is_deterministic(empty_buildings_gpkg, empty_trees_gpkg):
    lat = 48.5
    lon = 9.0
    elevation_m = 341.0
    timestamp = datetime(2024, 6, 21, 12, tzinfo=timezone.utc)
    tp1 = Trackpoint(lat=lat, lon=lon, elevation_m=elevation_m, timestamp=timestamp)
    tp2 = Trackpoint(lat=lat, lon=lon, elevation_m=elevation_m, timestamp=timestamp)

    result1 = shadow_index(tp1, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg)
    result2 = shadow_index(tp2, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg)
    assert result1 == result2


def test_batch_matches_scalar(empty_buildings_gpkg, empty_trees_gpkg):
    lat = [48.8, 49.0, 49.4, 49.8, 50.0, 51.0]
    lon = [7.8, 10.5, 9.0, 8.5, 7.9, 8.3]
    elevation_m = [341.0, 344.0, 130.0, 250.0, 285.0, 314.0]
    timestamp = datetime(2024, 6, 21, 12, tzinfo=timezone.utc)

    points = [
        Trackpoint(lat=lat[i], lon=lon[i], elevation_m=elevation_m[i], timestamp=timestamp)
        for i in range(len(lat))
    ]

    shadow_idx_list = shadow_index_many(
        points, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg
    )
    expected = [
        shadow_index(p, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg)
        for p in points
    ]
    assert shadow_idx_list == expected


def test_batch_empty_returns_empty(empty_buildings_gpkg, empty_trees_gpkg):
    empty_list = []
    shadow_idx_list_empty = shadow_index_many(
        empty_list, buildings_path=empty_buildings_gpkg, trees_path=empty_trees_gpkg
    )
    assert len(shadow_idx_list_empty) == 0