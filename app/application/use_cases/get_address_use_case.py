from app.application.dtos.geocoding_dto import GeocodingResultDTO
from app.domain.repositories.reverse_geocode_repository import ReverseGeocodeRepository


class GetAddressUseCase:
    def __init__(self, repository: ReverseGeocodeRepository):
        self.repository = repository

    def execute(self, latitude: float, longitude: float) -> GeocodingResultDTO:
        return self.repository.get_address(latitude, longitude)
