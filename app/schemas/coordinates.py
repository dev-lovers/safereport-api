from dataclasses import asdict

from pydantic import BaseModel

from app.domain.geocoding.entities.coordinates import CoordinateEntity


class CoordinateScheme(BaseModel):
    latitude: float
    longitude: float

    @classmethod
    def from_entity(cls, entity: CoordinateEntity):
        return cls(**asdict(entity))
