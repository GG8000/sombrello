from math import sin, radians

def uv_index_calculation(elevation_deg : float) -> float:
    # used approximation of UV index from https://doi.org/10.1111/j.1751-1097.2007.00200.x 
    # with avg of 300 DU of ozone from NASA https://ozonewatch.gsfc.nasa.gov/facts/dobson_SH.html
    return 12.5 * sin(radians(elevation_deg))**2.42 * (300 / 300)**(-1.23) if elevation_deg > 0 else 0
    
def uvi_effective(uv_index : float, shadow_index : float) -> float:
    return uv_index * (1 - shadow_index)