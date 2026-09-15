from datetime import datetime, timedelta, timezone
import pytest
import geopandas as gpd
from pydantic import ValidationError
from sombrello.models.trackpoint import Trackpoint, TrackMetadata
from sombrello.config import Settings
from sombrello.gpx import enrich, gpx_to_trackpoint_list, trackpoints_to_gpx, MissingTimestampError

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


@pytest.fixture
def empty_gis_settings(tmp_path) -> Settings:
    """Settings pointing at empty, temporary GIS datasets, so enrich()
    doesn't depend on real .gpkg files or environment variables."""
    buildings_path = tmp_path / "empty_buildings.gpkg"
    trees_path = tmp_path / "empty_trees.gpkg"

    empty_gdf = gpd.GeoDataFrame({"height": []}, geometry=[], crs="EPSG:4326")
    empty_gdf.to_file(buildings_path, driver="GPKG")
    empty_gdf.to_file(trees_path, driver="GPKG")

    return Settings(buildings_path=str(buildings_path), trees_path=str(trees_path))


def test_return_list():
    trackpoints_result, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert type(trackpoints_result) == list

def test_return_trackpoints_in_list():
    trackpoints_result, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert [type(trackpoints_result[i]) == Trackpoint for i in range(len(trackpoints_result))]

def test_return_list_length():
    trackpoints_result, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert len(trackpoints_result) == len(expected_trackpoints)

def test_list_objects():
    trackpoints_results, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert len(trackpoints_results) == len(expected_trackpoints)

    for res, exp in zip(trackpoints_results, expected_trackpoints):
        assert res.lat == pytest.approx(exp.lat)
        assert res.lon == pytest.approx(exp.lon)
        assert res.elevation_m == pytest.approx(exp.elevation_m)
        assert res.timestamp == pytest.approx(exp.timestamp, abs=timedelta(seconds=1))

def test_gpx_roundtrip_preserves_trackpoints(empty_gis_settings):
    original, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    enriched = [enrich(tp, empty_gis_settings) for tp in original]
    gpx = trackpoints_to_gpx(trackpoints=enriched, gpx_string=gpx_test_string, metadata=metadata)
    result, _ = gpx_to_trackpoint_list(gpx_string=gpx)
    assert result == original


def test_track_metadata_is_extracted():
    _, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert metadata.name == "Testroute-Sombrello"
    assert metadata.track_type == "hike"


def test_track_metadata_survives_roundtrip(empty_gis_settings):
    original, metadata = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    enriched = [enrich(tp, empty_gis_settings) for tp in original]
    gpx = trackpoints_to_gpx(trackpoints=enriched, gpx_string=gpx_test_string, metadata=metadata)
    _, result_metadata = gpx_to_trackpoint_list(gpx_string=gpx)
    assert result_metadata.name == metadata.name
    assert result_metadata.track_type == metadata.track_type


def test_track_and_segment_index_default_to_zero_for_single_segment():
    trackpoints, _ = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert all(tp.track_index == 0 for tp in trackpoints)
    assert all(tp.segment_index == 0 for tp in trackpoints)


def test_point_without_extensions_returns_empty_dict():
    trackpoints, _ = gpx_to_trackpoint_list(gpx_string=gpx_test_string)
    assert all(tp.extensions == {} for tp in trackpoints)

# --- Multi-segment + extensions fixture ---

gpx_multi_segment_string = """<?xml version='1.0' encoding='UTF-8'?>
<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:ext="https://example.com/ext/v1">
  <trk>
    <name>Multi-segment-test</name>
    <type>bike</type>
    <trkseg>
      <trkpt lat="48.5000" lon="9.0000">
        <ele>400.0</ele>
        <time>2026-08-25T08:00:00Z</time>
        <extensions>
          <ext:heartrate>120</ext:heartrate>
          <ext:cadence>85</ext:cadence>
        </extensions>
      </trkpt>
      <trkpt lat="48.5010" lon="9.0010">
        <ele>401.0</ele>
        <time>2026-08-25T08:00:10Z</time>
        <extensions>
          <ext:heartrate>122</ext:heartrate>
          <ext:cadence>86</ext:cadence>
        </extensions>
      </trkpt>
    </trkseg>
    <trkseg>
      <trkpt lat="48.5100" lon="9.0100">
        <ele>410.0</ele>
        <time>2026-08-25T08:30:00Z</time>
      </trkpt>
      <trkpt lat="48.5110" lon="9.0110">
        <ele>411.0</ele>
        <time>2026-08-25T08:30:10Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>"""


def test_multi_segment_indices_are_captured():
    trackpoints, _ = gpx_to_trackpoint_list(gpx_string=gpx_multi_segment_string)

    # First two points belong to segment 0, last two to segment 1, all track 0.
    assert [tp.segment_index for tp in trackpoints] == [0, 0, 1, 1]
    assert all(tp.track_index == 0 for tp in trackpoints)


def test_point_extensions_are_extracted():
    trackpoints, _ = gpx_to_trackpoint_list(gpx_string=gpx_multi_segment_string)

    assert trackpoints[0].extensions == {"heartrate": "120", "cadence": "85"}
    assert trackpoints[1].extensions == {"heartrate": "122", "cadence": "86"}
    # Points in the second segment have no extensions in the fixture.
    assert trackpoints[2].extensions == {}
    assert trackpoints[3].extensions == {}


def test_multi_segment_structure_survives_roundtrip(empty_gis_settings):
    original, metadata = gpx_to_trackpoint_list(gpx_string=gpx_multi_segment_string)
    enriched = [enrich(tp, empty_gis_settings) for tp in original]
    gpx = trackpoints_to_gpx(trackpoints=enriched, gpx_string=gpx_multi_segment_string, metadata=metadata)

    result, result_metadata = gpx_to_trackpoint_list(gpx_string=gpx)

    # Same number of points, same segment grouping as the original.
    assert [tp.segment_index for tp in result] == [tp.segment_index for tp in original]
    assert [tp.track_index for tp in result] == [tp.track_index for tp in original]
    assert result_metadata.name == "Multi-segment-test"
    assert result_metadata.track_type == "bike"


def test_point_extensions_survive_roundtrip(empty_gis_settings):
    original, metadata = gpx_to_trackpoint_list(gpx_string=gpx_multi_segment_string)
    enriched = [enrich(tp, empty_gis_settings) for tp in original]
    gpx = trackpoints_to_gpx(trackpoints=enriched, gpx_string=gpx_multi_segment_string, metadata=metadata)

    result, _ = gpx_to_trackpoint_list(gpx_string=gpx)

    assert result[0].extensions == {"heartrate": "120", "cadence": "85"}
    assert result[1].extensions == {"heartrate": "122", "cadence": "86"}

def test_missing_timestamp_raises_missing_timestamp_error():
    gpx_no_time = """<?xml version='1.0' encoding='UTF-8'?>
    <gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">
      <trk>
        <name>No-timestamp-test</name>
        <trkseg>
          <trkpt lat="48.5000" lon="9.0000">
            <ele>400.0</ele>
            <time>2026-08-25T08:00:00Z</time>
          </trkpt>
          <trkpt lat="48.5010" lon="9.0010">
            <ele>401.0</ele>
          </trkpt>
        </trkseg>
      </trk>
    </gpx>"""

    with pytest.raises(MissingTimestampError) as exc_info:
        gpx_to_trackpoint_list(gpx_string=gpx_no_time)

    assert exc_info.value.point_index == 1
    assert exc_info.value.track_index == 0
    assert exc_info.value.segment_index == 0
    assert "timestamp" in str(exc_info.value).lower()