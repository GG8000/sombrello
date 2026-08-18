from math import sin, radians

def uv_index_calculation(elevation_deg : float, altitude_m : float) -> float:
    return 12.5 * sin(radians(elevation_deg))**2.42 * (1 + 0.06 * (altitude_m / 1000)) if elevation_deg > 0 else 0
    
def uvi_effective(uv_index : float, shadow_index : float) -> float:
    return uv_index * (1 - shadow_index)