from uuid import uuid4
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, ValidationError
from sombrello.shadow import shadow_index
from sombrello.solar.solar import sun_position
from sombrello.uv import uv_index_calculation, uvi_effective
from sombrello.models.trackpoint import Trackpoint, TrackpointEnriched
from sombrello.gpx import enrich, gpx_to_trackpoint_list, trackpoints_to_gpx
from fastapi import Request
from gpxpy.gpx import GPXXMLSyntaxException
import json

class RouteData(BaseModel):
    """Saves raw data from route
    Attributes:
        trackpoints: List of the trackpoints from the route.
        gpx_string: Original gpx track as string
    """
    
    trackpoints : list[Trackpoint]
    gpx_string : str

# dict with routes which is available at runtime
_routes : dict[str, RouteData] = {}

router = APIRouter()

@router.get("/health")
def health():
    """Returns the current status of the API."""
    return {"status" : "ok"}

@router.post("/routes", status_code=201)
async def create_route(request : Request) -> dict:
    """Read and store a GPX route in memory.
    
    **Request body:**
    `Raw GPX content` as **UTF-8** encoded text.
    
    **Returns:**
    A JSON object containing the generated `route_id`.
    
    **Errors:**
    Returns HTTP `422` if the GPX content cannot be validated.
    """
    gpx_bytes = await request.body()
    gpx_string = gpx_bytes.decode("utf-8")
    try:
        list_trackpoints = gpx_to_trackpoint_list(gpx_string=gpx_string)
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except GPXXMLSyntaxException as e:
        raise HTTPException(status_code=422, detail=f"XML is malformed: {e}")
        
    route_id = str(uuid4())
    _routes[route_id] = RouteData(trackpoints=list_trackpoints,gpx_string=gpx_string)
    return {"route_id" : route_id}

@router.get("/routes/{id}")
def get_enriched_route(id : str) -> Response:
    """Return a route enriched with computed shadow data as GPX XML.

    **Path parameter:** `id`: ID of the route stored in memory.
    
    **Returns:**
    The enriched route with media type `application/gpx+xml`.

    **Errors:**
    Returns HTTP `404` if the route ID is not found.
    """
    if id not in _routes.keys(): 
        raise HTTPException(status_code=404, detail="Route not found") 
    
    trackpoints = _routes[id].trackpoints
    trackpoints_enriched = [enrich(tp) for tp in trackpoints]
    enriched_gpx = trackpoints_to_gpx(trackpoints=trackpoints_enriched, gpx_string=_routes[id].gpx_string)
    return Response(content=enriched_gpx, media_type="application/gpx+xml")

@router.get("/routes/{id}/json")
def get_enriched_route_json(id : str) -> list[TrackpointEnriched]:
    """Return a route enriched with computed shadow data as JSON.

    **Path parameter:** 
    `id`: ID of the route stored in memory.
    
    **Returns:**
    A list of enriched `TrackpointEnriched` objects.

    **Errors:**
    Returns HTTP `404` if the route ID is not found.
    """
    if id not in _routes.keys():
        raise HTTPException(status_code=404, detail="Route not found")
    
    trackpoints = _routes[id].trackpoints
    trackpoints_enriched = [enrich(tp) for tp in trackpoints]
    
    return trackpoints_enriched