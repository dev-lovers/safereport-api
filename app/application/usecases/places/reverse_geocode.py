from app.domain.repositories.google_maps import IGoogleMapsRepository


class ReverseGeocodeUseCase:
    def __init__(self, repository: IGoogleMapsRepository):
        self.repository = repository

    def execute(self, latitude: float, longitude: float):
        return self.repository.reverse_geocode(latitude, longitude)
