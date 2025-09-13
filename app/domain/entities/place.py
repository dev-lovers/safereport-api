from dataclasses import dataclass


@dataclass
class Place:
    id: str
    name: str
    address: str
    latitude: float
    longitude: float
