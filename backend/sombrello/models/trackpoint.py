from pydantic import BaseModel, Field
from datetime import datetime

class Trackpoint(BaseModel):
    lat : float = Field(ge=-90, le=90)
    lon : float = Field(ge=-180, le=180)
    elevation : float
    timestamp : datetime
