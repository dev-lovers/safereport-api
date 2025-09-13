import httpx

from fastapi import HTTPException
from app.core.config import settings

GEOCODE_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class GeocodeService:
    def geocode(self, address: str):
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
                    GEOCODE_API_URL,
                    params={"address": address, "key": settings.GOOGLE_MAPS_API_KEY},
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
                        detail="Não foi possível decodificar o endereço",
                    )

                coords = response_data["results"][0]["geometry"]["location"]
                lat = coords["lat"]
                lng = coords["lng"]
                return {"latitude": lat, "longitude": lng}

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
