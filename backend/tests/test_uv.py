from sombrello.uv import uv_index_calculation
import pytest


def test_zero_uv_when_sun_below_horizon():
    uv = uv_index_calculation(elevation_deg=0, altitude_km=0.5)
    assert uv == 0
    
def test_positive_uv_when_sun_over_horizon():
    uv = uv_index_calculation(elevation_deg=10, altitude_km=0.5)
    assert uv > 0
    
def test_overhead():
    uv = uv_index_calculation(elevation_deg=90, altitude_km=0)
    assert uv == pytest.approx(12.5, abs=0.1)
    
def test_monotonic():
    uv20 = uv_index_calculation(elevation_deg=20, altitude_km=0.5)
    uv45 = uv_index_calculation(elevation_deg=45, altitude_km=0.5)
    uv70 = uv_index_calculation(elevation_deg=70, altitude_km=0.5)
    assert uv20 < uv45
    assert uv20 < uv70
    assert uv45 < uv70
    
def test_altitude():
    uv0 = uv_index_calculation(elevation_deg=45, altitude_km=0)
    uv2000 = uv_index_calculation(elevation_deg=45, altitude_km=2)
    assert uv2000 > uv0