# tests/test_gis.py

import geopandas as gpd
from shapely.geometry import Polygon
import pytest

from sombrello.gis.buildings import get_nearby_buildings


@pytest.fixture
def fake_buildings_gpkg(tmp_path):
    """
    Creates a tiny throwaway .gpkg file with one known building,
    so the test doesn't depend on your real dataset.
    """
    square = Polygon([(11.575, 48.137), (11.576, 48.137), (11.576, 48.138), (11.575, 48.138)])
    gdf = gpd.GeoDataFrame({"height": [15.0]}, geometry=[square], crs="EPSG:4326")

    path = tmp_path / "test_buildings.gpkg"
    gdf.to_file(path, driver="GPKG")
    return str(path)


def test_get_nearby_buildings_finds_building_within_radius(fake_buildings_gpkg):
    result = get_nearby_buildings(
        lat=48.1375,
        lon=11.5755,
        radius_m=500,
        path=fake_buildings_gpkg,
    )
    assert len(result) == 1
    assert result[0].height_m == 15.0


def test_get_nearby_buildings_excludes_far_building(fake_buildings_gpkg):
    result = get_nearby_buildings(
        lat=10.0,   # far away — nowhere near the fake building
        lon=10.0,
        radius_m=500,
        path=fake_buildings_gpkg,
    )
    assert result == []