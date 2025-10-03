from app.domain.entities.address import Address
from app.domain.repositories.autocomplete_repository import AutocompleteRepository


class GetSuggestionsUseCase:
    def __init__(self, repository: AutocompleteRepository):
        self.repository = repository

    def execute(self, query: str) -> list[Address]:
        return self.repository.get_suggestions(query)
