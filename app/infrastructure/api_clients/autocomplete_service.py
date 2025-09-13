import httpx
from app.core.config import settings

AUTOCOMPLETE_API_URL = "https://places.googleapis.com/v1/places:searchText"


class AutocompleteService:

    def get_suggestions(self, query: str) -> list[str]:
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
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel",
        }

        try:
            with httpx.Client() as client:
                response = client.post(
                    AUTOCOMPLETE_API_URL,
                    json={"textQuery": query},
                    headers=headers,
                    timeout=10.0,
                )

                response.raise_for_status()
                response_data = response.json()

                suggestions = response_data.get("places", [])
                return suggestions

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha ao obter sugestões: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autocomplete: {e}"
            )
