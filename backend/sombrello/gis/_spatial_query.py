# gis/_spatial_query.py

import geopandas as gpd
from functools import lru_cache
from shapely.geometry import Point
from shapely.validation import make_valid


@lru_cache(maxsize=4)
def load_layer(path: str, layer: str | None = None) -> gpd.GeoDataFrame:
    gdf = gpd.read_file(path, layer=layer)

    if gdf.crs is not None and gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    gdf["geometry"] = gdf["geometry"].apply(
        lambda geom: make_valid(geom) if geom is not None and not geom.is_valid else geom
    )
    gdf = gdf[gdf["geometry"].notna() & gdf["geometry"].is_valid]

    return gdf


@lru_cache(maxsize=4)
def load_layer_projected(path: str, layer: str | None = None) -> gpd.GeoDataFrame:
    gdf = load_layer(path, layer=layer)
    projected = gdf.to_crs(epsg=3857)
    _ = projected.sindex  # force-build the spatial index once, up front
    return projected


def query_nearby(
    path: str,
    lat: float,
    lon: float,
    radius_m: float,
    layer: str | None = None,
) -> gpd.GeoDataFrame:
    gdf_m = load_layer_projected(path, layer=layer)

    point_m = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(epsg=3857).iloc[0]
    buffer = point_m.buffer(radius_m)

    # Use the spatial index to get only candidate rows near the buffer's
    # bounding box first, THEN do the precise intersects check on that
    # much smaller subset — instead of checking every row in the dataset.
    possible_idx = list(gdf_m.sindex.intersection(buffer.bounds))
    candidates = gdf_m.iloc[possible_idx]
    nearby = candidates[candidates.intersects(buffer)]

    return nearby.to_crs(epsg=4326)