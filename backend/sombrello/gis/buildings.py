from dataclasses import dataclass
from sombrello.gis._spatial_query import query_nearby


@dataclass(frozen=True)
class Building:
    """A single building footprint with a known height."""
    geometry: object  # shapely Polygon/MultiPolygon, in WGS84 (EPSG:4326)
    height_m: float


def get_nearby_buildings(
    lat: float,
    lon: float,
    radius_m: float,
    path: str,
    height_col: str = "height",
    layer: str | None = None,
) -> list[Building]:
    """
    Return buildings within `radius_m` metres of (lat, lon).

    Args:
        lat, lon: Query point in WGS84 degrees.
        radius_m: Search radius in metres.
        path: Path to the .gpkg file containing building footprints.
        height_col: Column name holding building height in metres.
        layer: Optional layer name, if the .gpkg has multiple layers.

    Returns:
        List of Building objects whose footprint falls within radius_m
        of the query point.
    """
    nearby = query_nearby(path, lat, lon, radius_m, layer=layer)

    buildings = []
    for geom, height in zip(nearby.geometry, nearby[height_col]):
        if height is None:
            continue
        buildings.append(Building(geometry=geom, height_m=float(height)))

    return buildings