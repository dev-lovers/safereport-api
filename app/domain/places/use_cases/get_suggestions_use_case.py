from app.infrastructure.api_clients.google_autocomplete_client import (
    AutocompleteService,
)
from app.schemas.suggestion import SuggestionScheme


class GetSuggestionsUseCase:

    def __init__(self, service: AutocompleteService = None):
        self.service = service or AutocompleteService()

    async def execute(self, query: str) -> list[SuggestionScheme]:
        try:
            suggestions = self.service.get_suggestions(query=query)
            return suggestions
        except Exception as e:
            raise RuntimeError(f"Erro ao obter sugestões: {str(e)}")
