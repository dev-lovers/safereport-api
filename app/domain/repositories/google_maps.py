from abc import ABC, abstractmethod

from app.domain.entities.place import Place
from app.domain.entities.coordinates import Coordinates
from app.domain.entities.address import Address


class IGoogleMapsRepository(ABC):

    @abstractmethod
    def search_place_autocomplete(self, query) -> list[Place]:
        raise NotImplementedError

    @abstractmethod
    def geocode(self, address: str) -> Coordinates:
        raise NotImplementedError

    @abstractmethod
    def reverse_geocode(self, latitude: float, longitude: float) -> Address:
        raise NotImplementedError
