from sombrello.shadow import shadow_index
from sombrello.solar.solar import sun_position
from sombrello.uv import uv_index_calculation, uvi_effective
from sombrello.models.trackpoint import Trackpoint, TrackpointEnriched, TrackMetadata
from sombrello.config import Settings, get_settings
from datetime import timezone
import gpxpy
import gpxpy.gpx
from lxml import etree


class MissingTimestampError(ValueError):
    """Raised when a GPX trackpoint has no <time> element.

    Sombrello requires a timestamp on every point to compute sun
    position, shadow, and UV values — a point without one cannot
    be enriched.
    """
    def __init__(self, point_index: int, track_index: int, segment_index: int):
        self.point_index = point_index
        self.track_index = track_index
        self.segment_index = segment_index
        super().__init__(
            f"Trackpoint {point_index} in track {track_index}, segment {segment_index} "
            f"has no timestamp. Sombrello requires a <time> element on every "
            f"trackpoint to compute sun position and shadow."
        )


def _extract_point_extensions(point: gpxpy.gpx.GPXTrackPoint) -> dict[str, str]:
    """Read arbitrary per-point <extensions> elements into a flat dict,
    excluding sombrello's own computed fields so a round trip doesn't
    reabsorb enrichment output as if it were original source data."""
    SOMBRELLO_NS = "https://sombrello.example/gpx/v1"

    extensions = {}
    for element in point.extensions:
        qname = etree.QName(element.tag)
        if qname.namespace == SOMBRELLO_NS:
            continue
        if element.text is not None:
            extensions[qname.localname] = element.text
    return extensions


def gpx_to_trackpoint_list(gpx_string: str) -> tuple[list[Trackpoint], TrackMetadata]:
    """Parse a GPX string into a flat list of trackpoints plus track-level metadata.

    Raises:
        MissingTimestampError: if any trackpoint has no <time> element.
    """
    gpx = gpxpy.parse(gpx_string)

    trackpoints = []
    metadata = TrackMetadata()

    for track_index, track in enumerate(gpx.tracks):
        if track_index == 0:
            metadata = TrackMetadata(
                name=track.name,
                description=track.description,
                track_type=track.type,
            )

        for segment_index, segment in enumerate(track.segments):
            for point_index, point in enumerate(segment.points):
                if point.time is None:
                    raise MissingTimestampError(point_index, track_index, segment_index)

                trackpoints.append(
                    Trackpoint(
                        lat=point.latitude,
                        lon=point.longitude,
                        elevation_m=point.elevation or 0.0,
                        timestamp=point.time,
                        track_index=track_index,
                        segment_index=segment_index,
                        extensions=_extract_point_extensions(point),
                    )
                )

    return trackpoints, metadata


def trackpoints_to_gpx(
    trackpoints: list[TrackpointEnriched],
    gpx_string: str,
    metadata: TrackMetadata | None = None,
) -> str:
    """Rebuild a GPX XML string from enriched trackpoints, preserving
    original track/segment structure, track-level metadata, and
    per-point extensions alongside the newly computed enrichment values."""
    NS = "https://sombrello.example/gpx/v1"
    gpx = gpxpy.parse(gpx_string)
    gpx.tracks = []

    metadata = metadata or TrackMetadata()

    grouped: dict[tuple[int, int], list[TrackpointEnriched]] = {}
    for tp in trackpoints:
        key = (tp.track_index, tp.segment_index)
        grouped.setdefault(key, []).append(tp)

    tracks_by_index: dict[int, gpxpy.gpx.GPXTrack] = {}

    for (track_idx, segment_idx), points in sorted(grouped.items()):
        if track_idx not in tracks_by_index:
            gpx_track = gpxpy.gpx.GPXTrack()
            if track_idx == 0:
                gpx_track.name = metadata.name
                gpx_track.description = metadata.description
                gpx_track.type = metadata.track_type
            gpx.tracks.append(gpx_track)
            tracks_by_index[track_idx] = gpx_track

        gpx_segment = gpxpy.gpx.GPXTrackSegment()
        tracks_by_index[track_idx].segments.append(gpx_segment)

        for tp in points:
            point = gpxpy.gpx.GPXTrackPoint(
                latitude=tp.lat,
                longitude=tp.lon,
                elevation=tp.elevation_m,
                time=tp.timestamp,
            )

            for name, value in tp.extensions.items():
                element = etree.Element(name)
                element.text = str(value)
                point.extensions.append(element)

            for name, value in [
                ("sun_elevation_deg", tp.sun_elevation_deg),
                ("shadow_index", tp.shadow_index),
                ("uv_index", tp.uv_index),
                ("uv_effective", tp.uv_effective),
            ]:
                element = etree.Element(f"{{{NS}}}{name}")
                element.text = str(value)
                point.extensions.append(element)

            gpx_segment.points.append(point)

    gpx.nsmap["sombrello"] = NS
    return gpx.to_xml(version="1.1")


def enrich(tp: Trackpoint, settings: Settings | None = None) -> TrackpointEnriched:
    """Enrich a single trackpoint with sun position, shadow, and UV data."""
    settings = settings or get_settings()
    sun = sun_position(tp.lat, tp.lon, tp.timestamp)
    shadow = shadow_index(
        tp,
        buildings_path=settings.buildings_path,
        trees_path=settings.trees_path,
    )
    uvi = uv_index_calculation(
        elevation_deg=sun.elevation_deg
    )
    return TrackpointEnriched(
        **tp.model_dump(),
        sun_elevation_deg=sun.elevation_deg,
        shadow_index=shadow,
        uv_index=uvi,
        uv_effective=uvi_effective(uvi, shadow)
    )