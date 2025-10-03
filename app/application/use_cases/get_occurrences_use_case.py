from typing import List

from app.domain.entities.occurrence import Occurrence
from app.domain.repositories.occurrence_repository import OccurrenceRepository


class GetOccurrencesUseCase:
    def __init__(self, repository: OccurrenceRepository):
        self.repository = repository

    def execute(self, city: str, state: str) -> List[Occurrence]:
        return self.repository.get_occurrences(city_id=city, state_id=state)
