# gis/buildings.py
from dataclasses import dataclass
from sombrello.gis._spatial_query import load_layer, query_nearby


@dataclass(frozen=True)
class Building:
    geometry: object
    height_m: float


def get_nearby_buildings(
    lat: float,
    lon: float,
    radius_m: float,
    path: str,
    height_col: str = "height",
    layer: str | None = None,
) -> list[Building]:
    gdf = load_layer(path, layer=layer)
    nearby = query_nearby(gdf, lat, lon, radius_m)

    buildings = []
    for geom, height in zip(nearby.geometry, nearby[height_col]):
        if height is None:
            continue
        buildings.append(Building(geometry=geom, height_m=float(height)))
    return buildings