from datetime import date, timedelta
from typing import Optional

import httpx
from fastapi import APIRouter, HTTPException, Depends, Cookie

from app.api.schemas.coordinates import CoordinateScheme
from app.core.config import settings
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.services.crossfire_auth_service import CrossfireAuthService
from app.services.occurrences_service import OccurrencesProcessor

from app.infrastructure.cache.redis import RedisClient, get_redis_client

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


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


@router.post("/")
async def get_occurrences(
    coordinates: CoordinateScheme,
    crossfire_auth_service: CrossfireAuthService = Depends(get_crossfire_auth_service),
    occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
    # TODO: Verificar uso futuro do cookie
    redis_client: RedisClient = Depends(get_redis_client),
    access_token: Optional[str] = Cookie(None),
):
    """
    Retorna as ocorrências brutas para a cidade/estado obtidos pela latitude e longitude.
    """
    try:
        city, state = await get_city_and_state(
            coordinates.latitude, coordinates.longitude
        )

        analysis_id = f"ocorrences_raw_{city.lower()}_{state.lower()}"

        cached_data = redis_client.get_json_cache(analysis_id)

        if cached_data:
            return {"message": "Hotspots (cached)", "data": cached_data}

        access_token = crossfire_auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API, settings.PASSWORD_CROSSFIRE_API
        )
        if not access_token:
            raise ValueError("Não foi possível obter o token de autenticação.")
        occurrence_gateway.set_access_token(access_token)

        today = date.today()
        final_date = today.strftime("%Y-%m-%d")
        initial_date = (today - timedelta(days=90)).strftime("%Y-%m-%d")

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


@router.post("/hotspots")
async def analyze_occurrences(
    location: CoordinateScheme,
    crossfire_auth_service: CrossfireAuthService = Depends(get_crossfire_auth_service),
    occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
    redis_client: RedisClient = Depends(get_redis_client),
    access_token: Optional[str] = Cookie(None),
):
    """
    Obtém e analisa hotspots de ocorrências com DBSCAN, utilizando cache Redis síncrono.
    """
    try:
        cidade, estado = await get_city_and_state(location.latitude, location.longitude)

        analysis_id = f"hotspot_{cidade.lower()}_{estado.lower()}"

        cached_data = redis_client.get_json_cache(analysis_id)

        if cached_data:
            print("Dados encontrados no cache Redis. Retornando dados em cache.")
            return {"message": "Hotspots (cached)", "data": cached_data}

        access_token = crossfire_auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API, settings.PASSWORD_CROSSFIRE_API
        )
        occurrence_gateway.set_access_token(access_token)

        today = date.today()
        final_date = today.strftime("%Y-%m-%d")
        initial_date = (today - timedelta(days=365)).strftime("%Y-%m-%d")

        occurrences = await occurrence_gateway.get_occurrences(
            city_name=cidade,
            state_name=estado,
            initial_date=initial_date,
            final_date=final_date,
        )

        processor = OccurrencesProcessor(epsilon_km=0.7, min_samples=8)
        analyzed_data = processor.cluster_occurrences(occurrences)

        redis_client.set_json_cache(analysis_id, analyzed_data, expire=172800)

        return {"message": "List of occurrence hotspots", "data": analyzed_data}

    except ConnectionRefusedError as e:
        raise HTTPException(
            status_code=503, detail=f"Serviço de Cache (Redis) indisponível: {str(e)}"
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}"
        )
