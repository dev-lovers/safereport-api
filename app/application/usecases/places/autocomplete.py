from app.domain.repositories.google_maps import IGoogleMapsRepository


class AutocompleteUseCase:
    def __init__(self, repository: IGoogleMapsRepository):
        self.repository = repository

    def execute(self, query: str):
        return self.repository.search_place_autocomplete(query)
