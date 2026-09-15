# sombrello/shadow/raycasting.py

import math

import geopandas as gpd
from shapely.affinity import translate
from shapely.geometry import Point
from shapely.ops import unary_union

from sombrello.solar.solar import sun_position, SolarPosition
from sombrello.gis.buildings import get_nearby_buildings
from sombrello.gis.trees import get_nearby_trees
from sombrello.models.trackpoint import Trackpoint


MIN_SUN_ELEVATION_DEG = 0.0


def required_search_radius(
    sun_elevation_deg: float,
    max_obstruction_height_m: float = 100.0,
    min_elevation_deg: float = 5.0,
) -> float:
    effective_elevation = max(sun_elevation_deg, min_elevation_deg)
    return max_obstruction_height_m / math.tan(math.radians(effective_elevation))


def _shadow_polygon(geometry_wgs84, height_m: float, sun: SolarPosition):
    """
    Compute the ground shadow polygon an obstruction casts, in EPSG:3857 metres.

    Method: translate the footprint along the shadow direction by the
    shadow length, then take the convex hull of footprint + translated
    copy. A plain union of the two would leave them disconnected if the
    shift is large relative to the footprint size; the hull guarantees
    a single valid connected polygon.
    """
    footprint_m = gpd.GeoSeries([geometry_wgs84], crs=4326).to_crs(epsg=3857).iloc[0]

    shadow_length_m = height_m / math.tan(math.radians(sun.elevation_deg))
    shadow_bearing_deg = (sun.azimuth_deg + 180) % 360  # shadow falls opposite the sun

    bearing_rad = math.radians(shadow_bearing_deg)
    dx = shadow_length_m * math.sin(bearing_rad)
    dy = shadow_length_m * math.cos(bearing_rad)

    shifted = translate(footprint_m, xoff=dx, yoff=dy)
    return unary_union([footprint_m, shifted]).convex_hull


def shadow_index(
    tp: Trackpoint,
    buildings_path: str,
    trees_path: str,
    max_obstruction_height_m: float = 100.0,
) -> float:
    """
    Binary shadow check: 1.0 if the point falls inside any obstruction's
    shadow polygon, 0.0 otherwise.
    """
    sun = sun_position(tp.lat, tp.lon, tp.timestamp)

    if sun.elevation_deg <= MIN_SUN_ELEVATION_DEG:
        return 1.0 

    radius = required_search_radius(sun.elevation_deg, max_obstruction_height_m)

    buildings = get_nearby_buildings(tp.lat, tp.lon, radius, path=buildings_path)
    trees = get_nearby_trees(tp.lat, tp.lon, radius, path=trees_path)

    point_m = gpd.GeoSeries([Point(tp.lon, tp.lat)], crs=4326).to_crs(epsg=3857).iloc[0]

    for obstruction in [*buildings, *trees]:
        shadow_poly = _shadow_polygon(obstruction.geometry, obstruction.height_m, sun)
        if shadow_poly.contains(point_m):
            return 1.0

    return 0.0


def shadow_index_many(
    points: list[Trackpoint],
    buildings_path: str,
    trees_path: str,
) -> list[float]:
    if len(points) == 0:
        return []
    return [shadow_index(tp, buildings_path, trees_path) for tp in points]