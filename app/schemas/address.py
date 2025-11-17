from dataclasses import asdict

from pydantic import BaseModel

from app.domain.geocoding.entities.address import AddressEntity


class AddressScheme(BaseModel):
    formatted_address: str

    @classmethod
    def from_entity(cls, entity: AddressEntity):
        return cls(**asdict(entity))
