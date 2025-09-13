import httpx

from fastapi import HTTPException
from app.core.config import settings

REVERSE_GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class ReverseGeocodeService:
    def reverse_geocode(self, latitude: float, longitude: float):
        try:
            with httpx.Client() as client:
                response = client.get(
                    REVERSE_GEOCODE_API_URL,
                    params={
                        "latlng": f"{latitude}, {longitude}",
                        "key": settings.GOOGLE_MAPS_API_KEY,
                    },
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                if (
                    response_data["status"] == "ZERO_RESULTS"
                    and not response_data["results"]
                ):
                    raise HTTPException(
                        status_code=404,
                        detail="Não foi encontrado um endereço para as coordenadas fornecidas",
                    )

                return {"address": response_data["results"][0]["formatted_address"]}

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
