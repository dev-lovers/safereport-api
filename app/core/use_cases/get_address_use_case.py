from app.core.interfaces.reverse_geocode_repository import ReverseGeocodeRepository


class GetAddressUseCase:
    def __init__(self, repository: ReverseGeocodeRepository):
        self.repository = repository

    def execute(self, latitude: float, longitude: float):
        return self.repository.get_address(latitude, longitude)
