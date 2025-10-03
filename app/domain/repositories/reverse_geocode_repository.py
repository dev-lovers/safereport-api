from abc import ABC, abstractmethod

from app.application.dtos.geocoding_dto import GeocodingResultDTO


class ReverseGeocodeRepository(ABC):
    @abstractmethod
    def get_address(self, latitude: float, longitude: float) -> GeocodingResultDTO:
        raise NotImplementedError
