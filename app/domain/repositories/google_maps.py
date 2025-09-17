from abc import ABC, abstractmethod

from app.domain.entities.address import Address
from app.domain.entities.coordinates import Coordinates


class IGoogleMapsRepository(ABC):

    @abstractmethod
    def search_place_autocomplete(self, query) -> list[Address]:
        raise NotImplementedError

    @abstractmethod
    def geocode(self, address: str) -> Address:
        raise NotImplementedError

    @abstractmethod
    def reverse_geocode(self, coordinates: Coordinates) -> Address:
        raise NotImplementedError
