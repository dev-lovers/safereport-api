from abc import ABC, abstractmethod

from app.domain.entities.occurrence import Occurrence


class OccurrenceGateway(ABC):

    @abstractmethod
    def get_occurrences(self, city_id: str, state_id: str) -> list[Occurrence]:
        pass
