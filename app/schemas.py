from typing import Any, List
from pydantic import BaseModel, validator, Field

class GeoJSON(BaseModel):
    type: str
    coordinates: List[float]

    @validator('type')
    def check_type(cls, v):
        if v != 'Point':
            raise ValueError('type must be Point')
        return v

    @validator('coordinates')
    def check_coordinates(cls, v):
        if len(v) != 2:
            raise ValueError('coordinates must contain two values')
        return v

class Trip(BaseModel):
    id: int
    region: str
    datetime: str
    origin_coord: GeoJSON
    destination_coord: GeoJSON
    datasource: str

class GroupedTrip(BaseModel):
    region: str
    origin_coord: GeoJSON  = Field(..., example={"type":"Point","coordinates":[14.4973794438195,50.00136875782316]})
    destination_coord: GeoJSON = Field(..., example={"type":"Point","coordinates":[14.43109483523328,50.04052930943246]})
    time_group: int
    average_hour: float
    count: int

    class Config:
        orm_mode = True

class WeeklyAverageRequest(BaseModel):
    min_longitude: float
    max_longitude: float
    min_latitude: float
    max_latitude: float
    region: str