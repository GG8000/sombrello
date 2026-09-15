from dataclasses import dataclass
from sombrello.gis._spatial_query import query_nearby


@dataclass(frozen=True)
class Tree:
    """A single tree canopy footprint with a known height."""
    geometry: object  # shapely Polygon/MultiPolygon, in WGS84 (EPSG:4326)
    height_m: float


def get_nearby_trees(
    lat: float,
    lon: float,
    radius_m: float,
    path: str,
    height_col: str = "height",
    layer: str | None = None,
) -> list[Tree]:
    """
    Return trees within `radius_m` metres of (lat, lon).

    Args:
        lat, lon: Query point in WGS84 degrees.
        radius_m: Search radius in metres.
        path: Path to the tree canopy vector file.
        height_col: Column name holding tree height in metres.
        layer: Optional layer name, if the file has multiple layers.

    Returns:
        List of Tree objects whose canopy falls within radius_m
        of the query point.
    """
    nearby = query_nearby(path, lat, lon, radius_m, layer=layer)

    trees = []
    for geom, height in zip(nearby.geometry, nearby[height_col]):
        if height is None:
            continue
        trees.append(Tree(geometry=geom, height_m=float(height)))

    return trees