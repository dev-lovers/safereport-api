from app.domain.repositories.google_maps import IGoogleMapsRepository


class GeocodeUseCase:
    def __init__(self, repository: IGoogleMapsRepository):
        self.repository = repository

    def execute(self, address: str):
        return self.repository.geocode(address)
