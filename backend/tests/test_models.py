from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from sombrello.models.trackpoint import Trackpoint

def test_trackpoint_holds_it_four_fields():
    tp = Trackpoint(lat=47.8, lon=13.04, elevation=424.0, timestamp=datetime(2024,6,21,12,tzinfo=timezone.utc))
    assert tp.lat == 47.8
    assert tp.lon == 13.04
    assert tp.elevation == 424.0
    assert tp.timestamp == datetime(2024,6,21,12,tzinfo=timezone.utc)
    
@pytest.mark.parametrize("lat", [-91.0,91.0])
def test_latitude_outside_the_globe_is_rejected(lat):
    with pytest.raises(ValidationError):
        Trackpoint(lat=lat, lon=0.0, elevation=0.0, timestamp=datetime(2024,6,21,12, tzinfo=timezone.utc))
        
@pytest.mark.parametrize("lon", [-181,181.0])
def test_longitude_outside_the_globe_is_rejected(lon):
    with pytest.raises(ValidationError):
        Trackpoint(lat=0.0, lon=lon, elevation=0.0, timestamp=datetime(2024,6,21,12,tzinfo=timezone.utc))