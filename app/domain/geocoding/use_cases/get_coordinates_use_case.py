from app.domain.geocoding.interfaces.geocode_repository import GeocodeRepository
from app.schemas.coordinates import CoordinateScheme


class GetCoordinatesUseCase:

    def __init__(self, repo: GeocodeRepository):
        self.repo = repo

    async def execute(self, address: str) -> CoordinateScheme:
        try:
            coordinates = await self.repo.get_coordinates(address)
            return coordinates
        except Exception as e:
            raise RuntimeError(f"Erro ao obter coordenadas: {e}")
