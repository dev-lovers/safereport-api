from abc import ABC, abstractmethod

from app.domain.entities.occurrence import Occurrence


class OccurrenceRepository(ABC):
    @abstractmethod
    def get_occurrences(self, city_id: str, state_id: str) -> list[Occurrence]:
        raise NotImplementedError
