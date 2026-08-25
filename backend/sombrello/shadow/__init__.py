from collections.abc import Sequence
import random

from sombrello.solar.solar import SolarPosition, sun_position
from sombrello.models.trackpoint import Trackpoint


def shadow_index(tp : Trackpoint) -> float:
    sun_pos : SolarPosition = sun_position(tp.lat, tp.lon, tp.timestamp)
    # Need to return a value between 0.0 and 1.0
    # TODO Need to be implemented, at the moment it is just a stub
    return random.randint(0,1)

def shadow_index_many(points : Sequence[Trackpoint]) -> list[float]:
    # TODO
    if len(points) == 0: 
        return []
    return [0.5,0.5,0.5,0.5,0.5,0.5]