from app.core.interfaces.geocode_repository import GeocodeRepository


class GetCoordinatesUseCase:
    def __init__(self, repository: GeocodeRepository):
        self.repository = repository

    def execute(self, address: str):
        return self.repository.get_coordinates(address)
