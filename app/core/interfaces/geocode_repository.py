from abc import ABC, abstractmethod


class GeocodeRepository(ABC):
    @abstractmethod
    def get_coordinates(self, address: str):
        raise NotImplementedError
