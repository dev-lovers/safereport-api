from pydantic import BaseModel


class GeocodingResultDTO(BaseModel):
    id: str
    formatted_address: str
    description: str
    latitude: float
    longitude: float
