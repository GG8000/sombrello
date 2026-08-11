from collections.abc import Sequence

from sombrello.models.trackpoint import Trackpoint


def shadow_index(tp : Trackpoint) -> float:
    # Need to return a value between 0.0 and 1.0
    # TODO Need to be implemented, at the moment it is just a stub
    return 0.5

def shadow_index_many(points : Sequence[Trackpoint]) -> list[float]:
    # TODO
    if len(points) == 0: 
        return []
    return [0.5,0.5,0.5,0.5,0.5,0.5]