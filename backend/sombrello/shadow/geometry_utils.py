import math

def required_search_radius(
    sun_elevation_deg: float,
    max_building_height_m: float = 53.3,
    min_elevation_deg: float = 5.0,
) -> float:
    """
    Compute how far away a building could still be tall enough to cast
    a shadow onto the query point, given current sun elevation.

    Args:
        sun_elevation_deg: Current sun elevation above horizon, in degrees.
        max_building_height_m: Tallest building height in Tuebingen's dataset.
        min_elevation_deg: Floor for elevation to avoid division blowing up
            near/below the horizon.

    Returns:
        Search radius in metres.
    """

    effective_elevation = max(sun_elevation_deg, min_elevation_deg)

    elevation_rad = math.radians(effective_elevation)
    return max_building_height_m / math.tan(elevation_rad)