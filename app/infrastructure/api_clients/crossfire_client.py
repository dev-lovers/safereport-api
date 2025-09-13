import httpx
from fastapi import HTTPException
from typing import Optional

from app.domain.entities.occurrence import Occurrence, OccurrenceFiltered
from app.domain.repositories.occurrence import OccurrenceGateway

CROSSFIRE_API_BASE_URL = "https://api-service.fogocruzado.org.br/api/v2"


class CrossfireAPIService(OccurrenceGateway):
    """
    Implementação concreta da OccurrenceGateway usando a API Crossfire.
    """

    def __init__(self):
        self._access_token: list[str] = None
        self._headers: dict = {}

    def set_access_token(self, access_token: str):
        """
        Define o token de acesso para as requisições.
        """
        self._access_token = access_token
        self._headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    def _get_state_id(self, state: str) -> Optional[str]:
        with httpx.Client() as client:
            response = client.get(
                f"{CROSSFIRE_API_BASE_URL}/states",
                headers=self._headers,
                timeout=10.0,
            )

            response.raise_for_status()
            response_data = response.json()
            data_payload = response_data.get("data", [])

            for state_info in data_payload:
                state_name = state_info.get("name").lower()
                if state_name == state.lower():
                    return state_info.get("id")

            return None

    def _get_city_id(self, city: str) -> Optional[str]:
        """
        Busca o ID da cidade a partir do nome. Método auxiliar interno.
        """
        city = city.upper()

        with httpx.Client() as client:
            params = {"cityName": city}
            response = client.get(
                f"{CROSSFIRE_API_BASE_URL}/cities",
                headers=self._headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            response_data = response.json()
            data_payload = response_data.get("data", [])

            for city_info in data_payload:
                city_name = city_info.get("name")
                if city_name.upper() == city:
                    return city_info.get("id")
            return None

    def get_occurrences(self, city_name: str, state_name: str) -> list[Occurrence]:
        """
        Busca ocorrências da API externa usando o nome da cidade e do estado.
        """
        if not self._access_token:
            raise ValueError("Token de acesso não configurado no serviço de API.")

        state_id = self._get_state_id(state_name)
        city_id = self._get_city_id(city_name)

        if not city_id:
            raise HTTPException(
                f"Localização '{city_name}, {state_name}' não encontrada."
            )

        with httpx.Client() as client:
            params = {
                "order": "ASC",
                "initialdate": "2025-07-04",
                "finaldate": "2025-08-04",
                "idState": state_id,
                "idCities": city_id,
            }

            response = client.get(
                f"{CROSSFIRE_API_BASE_URL}/occurrences",
                headers=self._headers,
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("code") != 200:
                raise HTTPException("Ocorrências não encontradas para a localização.")

            occurrences_raw = response_data.get("data", [])
            occurrences = [
                OccurrenceFiltered(
                    id=item.get("id"),
                    title=item.get("contextInfo", {})
                    .get("mainReason", {})
                    .get("name", ""),
                    latitude=item.get("latitude", 0.0),
                    longitude=item.get("longitude", 0.0),
                    description=item.get("contextInfo", {}).get("details", ""),
                    created_at=item.get("createdAt", ""),
                )
                for item in occurrences_raw
            ]
            return occurrences
