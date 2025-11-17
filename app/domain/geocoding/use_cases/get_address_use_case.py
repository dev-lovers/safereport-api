from app.domain.geocoding.interfaces.reverse_geocode_repository import (
    ReverseGeocodeRepository,
)
from app.schemas.address import AddressScheme


class GetAddressUseCase:

    def __init__(self, repo: ReverseGeocodeRepository):
        self.repo = repo

    async def execute(self, lat: float, lng: float) -> AddressScheme:
        try:
            address = await self.repo.get_address(lat, lng)
            return address
        except Exception as e:
            raise RuntimeError(f"Erro ao obter endereço reverso: {e}")
