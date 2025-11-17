from dataclasses import asdict

from pydantic import BaseModel

from app.domain.places.entities.suggestion import SuggestionEntity


class SuggestionScheme(BaseModel):
    id: str
    address: str
    description: str
    latitude: float
    longitude: float

    @classmethod
    def from_entity(cls, entity: SuggestionEntity):
        return cls(**asdict(entity))
