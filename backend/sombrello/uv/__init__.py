from math import sin, radians

def uv_index_calculation(elevation_deg, altitude_km):
    return 12.5 * sin(radians(elevation_deg))**2.42 * (1 + 0.06 * altitude_km) if elevation_deg > 0 else 0
    
    