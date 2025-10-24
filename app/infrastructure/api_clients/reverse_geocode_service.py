import httpx
from fastapi import HTTPException

from app.application.dtos.geocoding_dto import GeocodingResultDTO
from app.core.config import settings
from app.domain.repositories.reverse_geocode_repository import ReverseGeocodeRepository

GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class ReverseGeocodeService(ReverseGeocodeRepository):
    def get_address(self, latitude: float, longitude: float) -> GeocodingResultDTO:
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
            with httpx.Client() as client:
                response = client.get(
                    GEOCODING_API_URL,
                    params={
                        "latlng": f"{latitude}, {longitude}",
                        "key": settings.GOOGLE_MAPS_API_KEY,
                    },
                    timeout=10.0,
                )

                response.raise_for_status()
                reverse_geocode_response = response.json()

                if (
                    reverse_geocode_response["status"] == "ZERO_RESULTS"
                    and not reverse_geocode_response["results"]
                ):
                    raise HTTPException(
                        status_code=404,
                        detail="Não foi encontrado um endereço para as coordenadas fornecidas",
                    )

                # TODO: Revisar o nome da variável "most_compatible_address"
                most_compatible_address = reverse_geocode_response["results"][0]

                location_data = most_compatible_address["geometry"]["location"]
                resolved_latitude = location_data["lat"]
                resolved_longitude = location_data["lng"]

                street_name = ""
                for component in most_compatible_address.get("address_components", []):
                    if "route" in component.get("types", []):
                        street_name = component.get("long_name", "")

                reverse_geocode_result = GeocodingResultDTO(
                    id=reverse_geocode_response["results"][0].get("place_id", ""),
                    formatted_address=reverse_geocode_response["results"][0].get(
                        "formatted_address", ""
                    ),
                    description=street_name,
                    latitude=resolved_latitude,
                    longitude=resolved_longitude,
                )

                return reverse_geocode_result
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
