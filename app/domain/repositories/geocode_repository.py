from abc import ABC, abstractmethod

from app.application.dtos.geocoding_dto import GeocodingResultDTO


class GeocodeRepository(ABC):
    @abstractmethod
    def get_coordinates(self, address: str) -> GeocodingResultDTO:
        raise NotImplementedError
