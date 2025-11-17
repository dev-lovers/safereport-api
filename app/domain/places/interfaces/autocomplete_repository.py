from abc import ABC, abstractmethod

from app.domain.geocoding.entities.address import AddressEntity


class AutocompleteRepository(ABC):
    @abstractmethod
    def get_suggestions(self, query: str) -> list[AddressEntity]:
        raise NotImplementedError
