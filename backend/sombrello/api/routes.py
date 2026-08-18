from uuid import uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from sombrello.shadow import shadow_index
from sombrello.solar.solar import sun_position
from sombrello.uv import uv_index_calculation, uvi_effective
from sombrello.models.trackpoint import Trackpoint

class RouteRequest(BaseModel):
    trackpoints : list[Trackpoint]

_routes : dict[str, list[Trackpoint]] = {}

router = APIRouter()

@router.get("/health")
def health():
    return {"status" : "ok"}

@router.post("/routes", status_code=201)
def create_route(request : RouteRequest) -> dict:
    route_id = str(uuid4())
    _routes[route_id] = request.trackpoints
    return {"route_id" : route_id}

@router.get("/routes/{id}")
def get_enriched_route(id : str) -> dict:
    if id not in _routes.keys(): 
        raise HTTPException(status_code=404, detail="Route not found") 
    
    def _enrich(tp : Trackpoint) -> dict:
        sun = sun_position(tp.lat, tp.lon, tp.timestamp)
        shadow = shadow_index(tp)
        uvi = uv_index_calculation(
            elevation_deg=sun.elevation_deg,
            altitude_m=tp.elevation_m
        )
        return {
            "timestamp" : tp.timestamp,
            "elevation_deg" : sun.elevation_deg,
            "shadow_index" : shadow,
            "uv_index" : uvi,
            "uv_effective" : uvi_effective(uvi, shadow)
        }
    trackpoints = _routes[id]
    return {"trackpoints" : [_enrich(tp) for tp in trackpoints]}