from abc import ABC, abstractmethod


class ReverseGeocodeRepository(ABC):
    @abstractmethod
    def get_address(self, latitude: float, longitude: float):
        raise NotImplementedError
