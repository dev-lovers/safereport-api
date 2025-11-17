import httpx
from fastapi import HTTPException

from app.core.config import settings
from app.domain.geocoding.entities.address import AddressEntity
from app.domain.geocoding.interfaces.reverse_geocode_repository import (
    ReverseGeocodeRepository,
)

GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class ReverseGeocodeService(ReverseGeocodeRepository):

    async def get_address(self, latitude: float, longitude: float) -> AddressEntity:
        """
        Obtém o endereço formatado a partir das coordenadas de latitude e longitude.

        Args:
            latitude (float): Latitude do local.
            longitude (float): Longitude do local.

        Raises:
            httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
            httpx.RequestError: Se houver um problema de conexão com a API.
        """

        try:
            # Agora usando httpx.AsyncClient para chamadas assíncronas
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    GEOCODING_API_URL,
                    params={
                        "latlng": f"{latitude}, {longitude}",
                        "key": settings.GOOGLE_MAPS_API_KEY,
                    },
                )

            response.raise_for_status()
            reverse_geocode_response = response.json()

            # Caso nenhum endereço seja localizado
            if (
                reverse_geocode_response["status"] == "ZERO_RESULTS"
                and not reverse_geocode_response["results"]
            ):
                raise HTTPException(
                    status_code=404,
                    detail="Não foi encontrado um endereço para as coordenadas fornecidas",
                )

            # TODO: Revisar o nome da variável "most_compatible_address"
            # most_compatible_address = reverse_geocode_response["results"][0]

            # location_data = most_compatible_address["geometry"]["location"]
            # resolved_latitude = location_data["lat"]
            # resolved_longitude = location_data["lng"]

            # street_name = ""
            # for component in most_compatible_address.get("address_components", []):
            #     if "route" in component.get("types", []):
            #         street_name = component.get("long_name", "")

            reverse_geocode_result = AddressEntity(
                # id=reverse_geocode_response["results"][0].get("place_id", ""),
                formatted_address=reverse_geocode_response["results"][0].get(
                    "formatted_address", ""
                ),
                # description=street_name,
                # latitude=resolved_latitude,
                # longitude=resolved_longitude,
            )

            return reverse_geocode_result

        except httpx.HTTPStatusError as e:
            # Erro HTTP retornado pela API externa (400–599)
            raise ValueError(f"Falha ao obter sugestões: {e}") from e

        except httpx.RequestError as e:
            # Erro de rede (DNS, conexão, timeout, etc.)
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            ) from e
