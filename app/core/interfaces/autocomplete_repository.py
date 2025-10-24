from abc import ABC, abstractmethod

from app.core.entities.address import Address


class AutocompleteRepository(ABC):
    @abstractmethod
    def get_suggestions(self, query: str) -> list[Address]:
        raise NotImplementedError
