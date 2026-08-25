from sombrello.shadow import shadow_index
from sombrello.solar.solar import sun_position
from sombrello.uv import uv_index_calculation, uvi_effective
from sombrello.models.trackpoint import Trackpoint, TrackpointEnriched
from datetime import timezone
import gpxpy
import gpxpy.gpx
from lxml import etree

def gpx_to_trackpoint_list(gpx_string : str) -> list[Trackpoint]:
    gpx = gpxpy.parse(gpx_string)
    
    trackpoints = []
    
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                trackpoints.append(
                    Trackpoint(
                        lat=point.latitude,
                        lon=point.longitude,
                        elevation_m=point.elevation or 0.0,
                        timestamp=point.time or None
                        )
                    )
    return trackpoints

def trackpoints_to_gpx(trackpoints : list[TrackpointEnriched], gpx_string : str) -> str:
    NS = "https://sombrello.example/gpx/v1"
    gpx = gpxpy.parse(gpx_string)
    gpx.tracks = []
    gpx_track = gpxpy.gpx.GPXTrack()
    
    gpx.tracks.append(gpx_track)
    
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    for tp in trackpoints:
        point = gpxpy.gpx.GPXTrackPoint(
            latitude=tp.lat,
            longitude=tp.lon,
            elevation=tp.elevation_m,
            time=tp.timestamp,
        )
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

def enrich(tp : Trackpoint) -> TrackpointEnriched:
    sun = sun_position(tp.lat, tp.lon, tp.timestamp)
    shadow = shadow_index(tp)
    uvi = uv_index_calculation(
        elevation_deg=sun.elevation_deg,
        altitude_m=tp.elevation_m
    )
    return TrackpointEnriched(
        **tp.model_dump(),
        sun_elevation_deg = sun.elevation_deg,
        shadow_index = shadow,
        uv_index = uvi,
        uv_effective = uvi_effective(uvi, shadow)
    )
    