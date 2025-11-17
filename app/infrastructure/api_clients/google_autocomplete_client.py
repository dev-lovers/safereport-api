import httpx

from app.core.config import settings
from app.domain.places.entities.suggestion import SuggestionEntity
from app.domain.places.interfaces.autocomplete_repository import AutocompleteRepository

AUTOCOMPLETE_API_URL = "https://places.googleapis.com/v1/places:searchText"


class AutocompleteService(AutocompleteRepository):
    def get_suggestions(self, query: str) -> list[SuggestionEntity]:
        """
        Obtém sugestões de autocomplete da API.

        Args:
          query (str): O texto de consulta para o qual obter sugestões.

        Raises:
          httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
          httpx.RequestError: Se houver um problema de conexão com a API.
        """
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
            "X-Goog-FieldMask": "*",
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    AUTOCOMPLETE_API_URL,
                    json={
                        "textQuery": query,
                        "regionCode": "BR",
                        "languageCode": "pt-BR",
                        "locationBias": {
                            "circle": {
                                "center": {"latitude": -12.9777, "longitude": -38.5016},
                                "radius": 50000,
                            }
                        },
                    },
                    headers=headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                suggestions = response_data.get("places", [])

                new_suggestions = [
                    SuggestionEntity(
                        id=place.get("id", ""),
                        address=place.get("formattedAddress", ""),
                        description=place.get("displayName", {}).get("text", ""),
                        latitude=place.get("location", {}).get("latitude", 0.0),
                        longitude=place.get("location", {}).get("longitude", 0.0),
                    )
                    for place in suggestions
                ]

                return new_suggestions

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
