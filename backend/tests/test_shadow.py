import pytest
from datetime import datetime, timezone
from sombrello.solar.solar import sun_position
from sombrello.shadow import shadow_index, shadow_index_many
from sombrello.models.trackpoint import Trackpoint
import random



@pytest.fixture
def tp() -> Trackpoint:
    lat = 49.9
    lon = 10.6
    elevation_m = 1300.0
    timestamp = datetime(2024,6,21,12,tzinfo=timezone.utc)
    return Trackpoint(lat=lat,lon=lon,elevation_m=elevation_m,timestamp=timestamp)

def test_shadow_index_is_a_fraction(tp): 
    assert shadow_index(tp) >= 0.0
    assert shadow_index(tp) <= 1.0

def test_shadow_index_is_deterministic():
    lat = 48.5
    lon = 9.0
    elevation_m = 341.0
    timestamp = datetime(2024,6,21,12,tzinfo=timezone.utc)
    tp1 = Trackpoint(lat=lat,lon=lon,elevation_m=elevation_m,timestamp=timestamp)
    tp2 = Trackpoint(lat=lat,lon=lon,elevation_m=elevation_m,timestamp=timestamp)
    assert shadow_index(tp1) == shadow_index(tp2)
    

def test_batch_matches_scalar(): 
    lat = [48.8, 49.0, 49.4, 49.8, 50.0, 51.0]
    lon = [7.8, 10.5, 9.0, 8.5, 7.9, 8.3]
    elevation_m = [341.0, 344.0, 130.0, 250.0, 285.0, 314.0]
    timestamp = datetime(2024,6,21,12,tzinfo=timezone.utc)
    
    points = [Trackpoint(lat=lat[i], lon=lon[i], elevation_m=elevation_m[i], timestamp=timestamp) for i in range(len(lat))]
    shadow_idx_list = shadow_index_many(points)
    assert shadow_idx_list == [shadow_index(p) for p in points]

def test_batch_empty_returns_empty(): 
    empty_list = []
    shadow_idx_list_empty = shadow_index_many(empty_list)
    assert len(shadow_idx_list_empty) == 0

# @pytest.mark.xfail(reason="stub returns 0.0; Emil implements")
# def test_night_is_fully_shaded(): ...