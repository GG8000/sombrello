from datetime import datetime, timedelta, timezone
import pytest
from pydantic import ValidationError
from sombrello.models.trackpoint import Trackpoint
from sombrello.gpx import enrich, gpx_to_trackpoint_list, trackpoints_to_gpx

gpx_test_string = "<?xml version='1.0' encoding='UTF-8'?>\n<gpx version=\"1.1\" creator=\"https://www.komoot.de\" xmlns=\"http://www.topografix.com/GPX/1/1\" xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:schemaLocation=\"http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd\">\n  <metadata>\n    <name>Testroute-Sombrello</name>\n    <author>\n      <link href=\"https://www.komoot.de\">\n        <text>komoot</text>\n        <type>text/html</type>\n      </link>\n    </author>\n  </metadata>\n  <wpt lat=\"48.545926\" lon=\"9.057296\">\n    <name>T\u00fcbingen Ulmenweg</name>\n    <sym>Flag, Blue</sym>\n  </wpt>\n  <wpt lat=\"48.551085\" lon=\"9.050721\">\n    <name>Naturlehrpfad im Naturpark Sch\u00f6nbuch</name>\n    <sym>Flag, Blue</sym>\n  </wpt>\n  <trk>\n    <name>Testroute-Sombrello</name>\n    <type>hike</type>\n    <trkseg>\n        <trkpt lat=\"48.550598\" lon=\"9.050343\">\n        <ele>485.596578</ele>\n        <time>2026-08-25T15:19:09.050Z</time>\n      </trkpt>\n      <trkpt lat=\"48.550807\" lon=\"9.050360\">\n        <ele>485.596578</ele>\n        <time>2026-08-25T15:19:31.142Z</time>\n      </trkpt>\n      <trkpt lat=\"48.550933\" lon=\"9.050497\">\n        <ele>485.596578</ele>\n        <time>2026-08-25T15:19:47.451Z</time>\n      </trkpt>\n      <trkpt lat=\"48.551043\" lon=\"9.050754\">\n        <ele>485.596578</ele>\n        <time>2026-08-25T15:20:08.534Z</time>\n      </trkpt>\n      <trkpt lat=\"48.551075\" lon=\"9.050706\">\n        <ele>485.596578</ele>\n        <time>2026-08-25T15:20:13.258Z</time>\n      </trkpt>\n    </trkseg>\n  </trk>\n</gpx>"
expected_trackpoints = [
    Trackpoint(
        lat=48.550598,
        lon=9.050343,
        elevation_m=485.596578,
        timestamp=datetime.fromisoformat("2026-08-25T15:19:09.050Z")
    ),
    Trackpoint(
        lat=48.550807,
        lon=9.050360,
        elevation_m=485.596578,
        timestamp=datetime.fromisoformat("2026-08-25T15:19:31.142Z")
    ),
    Trackpoint(
        lat=48.550933,
        lon=9.050497,
        elevation_m=485.596578,
        timestamp=datetime.fromisoformat("2026-08-25T15:19:47.451Z")
    ),
    Trackpoint(
        lat=48.551043,
        lon=9.050754,
        elevation_m=485.596578,
        timestamp=datetime.fromisoformat("2026-08-25T15:20:08.534Z")
    ),
    Trackpoint(
        lat=48.551075,
        lon=9.050706,
        elevation_m=485.596578,
        timestamp=datetime.fromisoformat("2026-08-25T15:20:13.258Z")
    )   
]

def test_return_list():
    trackpoints_result = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert type(trackpoints_result) == list
    
def test_return_trackpoints_in_list():
    trackpoints_result = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert [type(trackpoints_result[i]) == Trackpoint for i in range(len(trackpoints_result))]
    
def test_return_list_length():
    trackpoints_result = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert len(trackpoints_result) == len(expected_trackpoints)

def test_list_objects():
    trackpoints_results = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert len(trackpoints_results) == len(expected_trackpoints)
    
    for res, exp in zip(trackpoints_results, expected_trackpoints):
        assert res.lat == pytest.approx(exp.lat)
        assert res.lon == pytest.approx(exp.lon)
        assert res.elevation_m == pytest.approx(exp.elevation_m)
        assert res.timestamp == pytest.approx(exp.timestamp, abs=timedelta(seconds=1))
    
def test_gpx_roundtrip_preserves_trackpoints():
    original = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    enriched = [enrich(tp) for tp in original]
    gpx = trackpoints_to_gpx(trackpoints=enriched, gpx_string=gpx_test_string)
    result = gpx_to_trackpoint_list(gpx_string=gpx)
    assert result == original
    