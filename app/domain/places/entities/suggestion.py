from dataclasses import dataclass


@dataclass
class SuggestionEntity:
    id: str
    address: str
    description: str
    latitude: float
    longitude: float
