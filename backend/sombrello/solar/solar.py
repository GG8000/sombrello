from dataclasses import dataclass
from datetime import datetime
import pvlib
import pandas as pd
from sombrello.models.trackpoint import Trackpoint

@dataclass(frozen=True)
class SolarPosition:
    azimuth_deg : float
    elevation_deg : float
    
def sun_position(lat : float, lon : float, when: datetime) -> SolarPosition:
    times = pd.DatetimeIndex([when])
    result = pvlib.solarposition.get_solarposition(times, lat, lon)
    return SolarPosition(
        azimuth_deg=float(result["azimuth"].iloc[0]),
        elevation_deg=float(result["apparent_elevation"].iloc[0]))
    
def sun_positions(trackpoints : list[Trackpoint]) -> list[SolarPosition]:
    sun_positions : list[Trackpoint] = []
    for tp in trackpoints:
        sun_positions.append(sun_position(tp.lat, tp.lon, tp.timestamp))
        
    return sun_positions