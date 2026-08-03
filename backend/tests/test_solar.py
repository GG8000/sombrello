from datetime import datetime, timezone
from sombrello.solar.solar import sun_position


SALZBURG = (47.80, 13.04)

def test_sun_is_below_horizon_at_local_midnight():
    pos = sun_position(*SALZBURG, datetime(2024,6,21,0,tzinfo=timezone.utc))
    assert pos.elevation_deg < 0
    
def test_sun_is_almost_overhead_at_the_equator_on_the_equinox():
    pos = sun_position(0.0,0.0, datetime(2024,3,20,12,tzinfo=timezone.utc))
    assert pos.elevation_deg > 85
    
def test_azimuth_is_a_compass_bearing():
    pos = sun_position(*SALZBURG, datetime(2024,6,21,12, tzinfo=timezone.utc))
    assert 0 <= pos.azimuth_deg <= 360