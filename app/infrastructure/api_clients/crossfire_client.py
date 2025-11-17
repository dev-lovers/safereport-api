import asyncio

import httpx
from fastapi import HTTPException

from app.domain.occurrences.entities.occurrence import Occurrence
from app.domain.occurrences.interfaces.occurrence_repository import OccurrenceRepository

CROSSFIRE_API_BASE_URL = "https://api-service.fogocruzado.org.br/api/v2"


class CrossfireAPIService(OccurrenceRepository):

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

    def _get_state_id(self, state: str) -> str | None:
        """
        Busca o ID do estado a partir do nome. Método auxiliar interno.

        Args:
                                        state (str): Nome do estado (ex: "São Paulo").
        Returns:
                                        Optional[str]: ID do estado se encontrado, caso contrário None.
        """
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

    def _get_city_id(self, city: str) -> str | None:
        """
        Busca o ID da cidade a partir do nome. Método auxiliar interno.

        Args:
                                        city (str): Nome da cidade (ex: "São Paulo").
        Returns:
                                        Optional[str]: ID da cidade se encontrado, caso contrário None.
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

    async def get_occurrences(
        self, city_name: str, state_name: str, initial_date: str, final_date: str
    ) -> list[Occurrence]:
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

        max_pages = 25

        take = 150
        occurrences = []

        async with httpx.AsyncClient(timeout=10.0) as client:
            tasks = []

            for page in range(1, max_pages + 1):
                params = {
                    "order": "ASC",
                    "initialdate": initial_date,
                    "finaldate": final_date,
                    "idState": state_id,
                    "idCities": city_id,
                    "take": take,
                    "page": page,
                }
                tasks.append(
                    client.get(
                        f"{CROSSFIRE_API_BASE_URL}/occurrences",
                        headers=self._headers,
                        params=params,
                    )
                )

            responses = await asyncio.gather(*tasks, return_exceptions=True)

            for page, response in enumerate(responses, start=1):
                if isinstance(response, Exception):
                    print(f"❌ Erro na página {page}: {response}")
                    continue

                response.raise_for_status()
                data = response.json()

                if data.get("code") != 200:
                    print(f"⚠️ Página {page} não retornou código 200")
                    continue

                occurrences_raw = data.get("data", [])
                occurrences.extend(occurrences_raw)

                # early stop: se veio menos do que o esperado, acabou
                if len(occurrences_raw) < take:
                    break

        return occurrences
