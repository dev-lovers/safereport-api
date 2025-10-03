from app.application.dtos.geocoding_dto import GeocodingResultDTO
from app.domain.repositories.geocode_repository import GeocodeRepository


class GetCoordinatesUseCase:
    def __init__(self, repository: GeocodeRepository):
        self.repository = repository

    def execute(self, address: str) -> GeocodingResultDTO:
        return self.repository.get_coordinates(address)
