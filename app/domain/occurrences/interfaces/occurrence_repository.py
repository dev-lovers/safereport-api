from abc import ABC, abstractmethod

from app.domain.occurrences.entities.occurrence import Occurrence


class OccurrenceRepository(ABC):
    @abstractmethod
    def get_occurrences(
        self, city_id: str, state_id: str, initial_date: str, final_date: str
    ) -> list[Occurrence]:
        raise NotImplementedError
