from pydantic import BaseModel


class CoordinateScheme(BaseModel):
    latitude: float
    longitude: float
