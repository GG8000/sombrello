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

def query_nearby(gdf: gpd.GeoDataFrame, lat: float, lon: float, radius_m: float) -> gpd.GeoDataFrame:
    gdf_m = gdf.to_crs(epsg=3857)
    point_m = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(epsg=3857).iloc[0]
    buffer = point_m.buffer(radius_m)
    nearby = gdf_m[gdf_m.intersects(buffer)]
    return nearby.to_crs(epsg=4326) 