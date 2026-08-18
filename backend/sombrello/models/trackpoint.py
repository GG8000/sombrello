from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone

class Trackpoint(BaseModel):
    lat : float = Field(ge=-90, le=90)
    lon : float = Field(ge=-180, le=180)
    elevation_m : float = Field(ge=-500)
    timestamp : datetime
    
