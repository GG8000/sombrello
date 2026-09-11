# gis/trees.py
from dataclasses import dataclass
from sombrello.gis._spatial_query import load_layer, query_nearby


@dataclass(frozen=True)
class Tree:
    geometry: object
    height_m: float


def get_nearby_trees(
    lat: float,
    lon: float,
    radius_m: float,
    path: str,
    height_col: str = "height",
    layer: str | None = None,
) -> list[Tree]:
    gdf = load_layer(path, layer=layer)
    nearby = query_nearby(gdf, lat, lon, radius_m)

    trees = []
    for geom, height in zip(nearby.geometry, nearby[height_col]):
        if height is None:
            continue
        trees.append(Tree(geometry=geom, height_m=float(height)))
    return trees