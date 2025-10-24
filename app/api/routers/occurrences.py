import json
from datetime import date, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.schemas.coordinates import CoordinateScheme
from app.config import settings
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.auth.crossfire_auth_service import CrossfireAuthService
from app.infrastructure.cache.redis_cache_service import RedisClient, get_redis_client

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


CACHE_KEY = "analysis_result_salvador"


def get_crossfire_auth_service() -> CrossfireAuthService:
    return CrossfireAuthService()


def get_occurrence_gateway() -> CrossfireAPIService:
    return CrossfireAPIService()


async def get_city_and_state(latitude: float, longitude: float) -> tuple[str, str]:
    """
    Obtém cidade e estado a partir da latitude e longitude usando a API do Google.
    """
    url = (
        f"https://maps.googleapis.com/maps/api/geocode/json"
        f"?latlng={latitude},{longitude}&key={settings.GOOGLE_MAPS_API_KEY}"
    )
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

    cidade = estado = None
    if data["status"] == "OK":
        for component in data["results"][0]["address_components"]:
            if "administrative_area_level_2" in component["types"]:
                cidade = component["long_name"]
            if "administrative_area_level_1" in component["types"]:
                estado = component["long_name"]

    if not cidade or not estado:
        raise HTTPException(
            status_code=404,
            detail="Cidade ou estado não encontrados para as coordenadas fornecidas.",
        )

    return cidade, estado


@router.get("/")
async def get_occurrences(
    coordinates: CoordinateScheme = Depends(),
    crossfire_auth_service: CrossfireAuthService = Depends(get_crossfire_auth_service),
    occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
    redis_client: RedisClient = Depends(get_redis_client),
):
    """
    Retorna as ocorrências brutas para a cidade/estado obtidos pela latitude e longitude.
    """
    try:
        days_to_search = 31

        city, state = await get_city_and_state(
            coordinates.latitude, coordinates.longitude
        )

        today = date.today()
        today_str = today.strftime("%Y-%m-%d")

        analysis_id = (
            f"ocorrences_raw_{city.lower()}_{state.lower()}"
            f"_{today_str}_last{days_to_search}days"
        )

        cached_data = redis_client.get_json_cache(analysis_id)

        if cached_data:
            return {"message": "Raw occurrences list (cached)", "data": cached_data}

        access_token = crossfire_auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API, settings.PASSWORD_CROSSFIRE_API
        )
        if not access_token:
            raise ValueError("Não foi possível obter o token de autenticação.")
        occurrence_gateway.set_access_token(access_token)

        final_date = today_str
        initial_date = (today - timedelta(days=days_to_search)).strftime("%Y-%m-%d")

        occurrences = await occurrence_gateway.get_occurrences(
            city_name=city,
            state_name=state,
            initial_date=initial_date,
            final_date=final_date,
        )

        redis_client.set_json_cache(analysis_id, occurrences, expire=3600)

        return {"message": "Raw occurrences list", "data": occurrences}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        status_code = (
            exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else 503
        )
        detail = (
            f"Erro na API do CrossFire. {exc.response.text}"
            if isinstance(exc, httpx.HTTPStatusError)
            else "Não foi possível conectar à API do CrossFire no momento."
        )
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}"
        )


@router.get("/hotspots")
def get_hotspots(
    redis_client: RedisClient = Depends(get_redis_client),
):
    """
    Obtém a análise de hotspots de ocorrências mais recente.

    Estes dados são pré-processados por um worker em segundo plano
    e armazenados em cache para entrega imediata.
    """
    try:
        if not redis_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de cache indisponível.",
            )

        cached_data_str = redis_client.get_data(CACHE_KEY)

        if cached_data_str is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Nenhum resultado de análise encontrado. O processamento inicial pode estar em andamento.",
            )

        try:
            analysis_data_dict = json.loads(cached_data_str)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar dados do cache. Formato inválido.",
            )

        return {
            "message": "Análise de hotspots obtida com sucesso",
            "data": analysis_data_dict,
        }

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro inesperado no servidor.",
        )
