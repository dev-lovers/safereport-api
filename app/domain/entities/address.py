from dataclasses import dataclass


@dataclass
class Address:
    id: str
    address: str
    description: str
    latitude: float
    longitude: float
