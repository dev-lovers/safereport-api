from datetime import date, timedelta

import httpx
from app.core.config import settings
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.auth.crossfire_auth_service import CrossfireAuthService
from app.infrastructure.cache.redis_cache_service import RedisClient
from app.schemas.coordinates import CoordinateScheme
from fastapi import HTTPException

GEOCODING_API_URL = "https://maps.googleapis.com/maps/api/geocode/json"


class GetOccurrencesUseCase:
    """
    Use case responsável por:
    - Descobrir cidade/estado via coordenadas (Google Geocoding)
    - Montar chave de cache p/ resultado
    - Verificar cache no Redis
    - Autenticar na CrossFire API
    - Buscar ocorrências na CrossFire
    - Atualizar o cache
    """

    def __init__(
        self,
        auth_service: CrossfireAuthService,
        occurrence_gateway: CrossfireAPIService,
        redis_client: RedisClient,
    ) -> None:
        self.auth_service = auth_service
        self.occurrence_gateway = occurrence_gateway
        self.redis_client = redis_client
        self.days_to_search = 31

    async def execute(self, coordinates: CoordinateScheme) -> list[dict]:
        # 1) Obter cidade/estado a partir de lat/lng
        city, state = await self._get_city_and_state(
            coordinates.latitude,
            coordinates.longitude,
        )

        # 2) Datas de busca
        today = date.today()
        today_str = today.strftime("%Y-%m-%d")
        initial_date = (today - timedelta(days=self.days_to_search)).strftime(
            "%Y-%m-%d"
        )

        # 3) Montar chave de cache
        analysis_id = (
            f"ocorrences_raw_{city.lower()}_{state.lower()}"
            f"_{today_str}_last{self.days_to_search}days"
        )

        # 4) Verificar cache
        cached_data = self.redis_client.get_json_cache(analysis_id)
        if cached_data:
            # Mantém o mesmo formato anterior, apenas devolvendo os dados
            return cached_data

        # 5) Autenticar na CrossFire
        access_token = self.auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API,
            settings.PASSWORD_CROSSFIRE_API,
        )
        if not access_token:
            raise ValueError("Não foi possível obter o token de autenticação.")

        self.occurrence_gateway.set_access_token(access_token)

        # 6) Buscar ocorrências na CrossFire API
        occurrences = await self.occurrence_gateway.get_occurrences(
            city_name=city,
            state_name=state,
            initial_date=initial_date,
            final_date=today_str,
        )

        # 7) Atualizar cache
        self.redis_client.set_json_cache(analysis_id, occurrences, expire=3600)

        return occurrences

    async def _get_city_and_state(
        self, latitude: float, longitude: float
    ) -> tuple[str, str]:
        """
        Obtém cidade e estado a partir da latitude e longitude usando a API do Google.
        (Lógica que antes estava na rota foi movida para o use case)
        """
        url = (
            f"{GEOCODING_API_URL}"
            f"?latlng={latitude},{longitude}&key={settings.GOOGLE_MAPS_API_KEY}"
        )

        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

        cidade = estado = None
        if data.get("status") == "OK" and data.get("results"):
            for component in data["results"][0].get("address_components", []):
                if "administrative_area_level_2" in component.get("types", []):
                    cidade = component.get("long_name")
                if "administrative_area_level_1" in component.get("types", []):
                    estado = component.get("long_name")

        if not cidade or not estado:
            raise HTTPException(
                status_code=404,
                detail=(
                    "Cidade ou estado não encontrados para as coordenadas fornecidas."
                ),
            )

        return cidade, estado
