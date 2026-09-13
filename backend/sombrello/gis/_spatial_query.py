import geopandas as gpd
from functools import lru_cache
from shapely.geometry import Point
from shapely.validation import make_valid


@lru_cache(maxsize=4)
def load_layer(path: str, layer: str | None = None) -> gpd.GeoDataFrame:
    """
    Load and cache a vector layer, reprojected to WGS84 (EPSG:4326)
    with invalid geometries repaired.
    """
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
    """
    Same as load_layer, but pre-reprojected to EPSG:3857 (metres) and
    cached separately, so repeated spatial queries don't re-reproject
    the whole dataset on every call.
    """
    gdf = load_layer(path, layer=layer)
    return gdf.to_crs(epsg=3857)


def query_nearby(
    path: str,
    lat: float,
    lon: float,
    radius_m: float,
    layer: str | None = None,
) -> gpd.GeoDataFrame:
    """
    Return features within radius_m metres of (lat, lon), in WGS84.
    """
    gdf_m = load_layer_projected(path, layer=layer)

    point_m = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(epsg=3857).iloc[0]
    buffer = point_m.buffer(radius_m)
    nearby = gdf_m[gdf_m.intersects(buffer)]

    return nearby.to_crs(epsg=4326)