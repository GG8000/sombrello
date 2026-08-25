from uuid import uuid4

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, ValidationError

from sombrello.shadow import shadow_index
from sombrello.solar.solar import sun_position
from sombrello.uv import uv_index_calculation, uvi_effective
from sombrello.models.trackpoint import Trackpoint, TrackpointEnriched
from sombrello.gpx import enrich, gpx_to_trackpoint_list, trackpoints_to_gpx
from fastapi import Request
import json

class RouteData(BaseModel):
    trackpoints : list[Trackpoint]
    gpx_string : str

_routes : dict[str, RouteData] = {}

router = APIRouter()

@router.get("/health")
def health():
    return {"status" : "ok"}

@router.post("/routes", status_code=201)
async def create_route(request : Request) -> dict:
    gpx_bytes = await request.body()
    gpx_string = gpx_bytes.decode("utf-8")
    try:
        list_trackpoints = gpx_to_trackpoint_list(gpx_string=gpx_string)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    route_id = str(uuid4())
    _routes[route_id] = RouteData(trackpoints=list_trackpoints,gpx_string=gpx_string)
    return {"route_id" : route_id}

@router.get("/routes/{id}")
def get_enriched_route(id : str) -> Response:
    if id not in _routes.keys(): 
        raise HTTPException(status_code=404, detail="Route not found") 
    
    trackpoints = _routes[id].trackpoints
    trackpoints_enriched = [enrich(tp) for tp in trackpoints]
    enriched_gpx = trackpoints_to_gpx(trackpoints=trackpoints_enriched, gpx_string=_routes[id].gpx_string)
    return Response(content=enriched_gpx, media_type="application/gpx+xml")

@router.get("/routes/{id}/json")
def get_enriched_route_json(id : str) -> list[TrackpointEnriched]:
    if id not in _routes.keys():
        raise HTTPException(status_code=404, detail="Route not found")
    
    trackpoints = _routes[id].trackpoints
    trackpoints_enriched = [enrich(tp) for tp in trackpoints]
    
    return trackpoints_enriched