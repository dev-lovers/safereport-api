import httpx
from fastapi import HTTPException

from app.application.dtos.geocoding_dto import GeocodingResultDTO
from app.core.config import settings
from app.domain.repositories.geocode_repository import GeocodeRepository

GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class GeocodeService(GeocodeRepository):
    def get_coordinates(self, address: str) -> GeocodingResultDTO:
        """
        Obtém as coordenadas (latitude e longitude) para um endereço fornecido.

        Args:
            address (str): O endereço a ser geocodificado.
        Raises:
            httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
            httpx.RequestError: Se houver um problema de conexão com a API.
            HTTPException: Se o endereço não puder ser decodificado.
        """
        try:
            with httpx.Client() as client:
                response = client.get(
                    GEOCODING_API_URL,
                    params={"address": address, "key": settings.GOOGLE_MAPS_API_KEY},
                    timeout=10.0,
                )

                response.raise_for_status()
                geocode_response = response.json()

                if (
                        geocode_response["status"] == "ZERO_RESULTS"
                        and not geocode_response["results"]
                ):
                    raise HTTPException(
                        status_code=404,
                        detail="Não foi possível decodificar o endereço",
                    )

                # TODO: Revisar o nome da variável "most_compatible_address"
                most_compatible_address = geocode_response["results"][0]

                location_data = most_compatible_address["geometry"]["location"]
                latitude = location_data["lat"]
                longitude = location_data["lng"]

                street_name = ""
                for component in most_compatible_address.get("address_components", []):
                    if "route" in component.get("types", []):
                        street_name = component.get("long_name", "")

                geocode_result = GeocodingResultDTO(
                    id=most_compatible_address.get("place_id", ""),
                    formatted_address=most_compatible_address.get("formatted_address", ""),
                    description=street_name,
                    latitude=latitude,
                    longitude=longitude,
                )

                return geocode_result

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
