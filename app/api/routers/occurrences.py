import time
from datetime import date, timedelta
from typing import Optional

import folium
import httpx
from fastapi import APIRouter, HTTPException, Depends, Cookie
from fastapi.responses import HTMLResponse

from app.api.schemas.location import LocationSchema
from app.core.config import settings
from app.infrastructure.api_clients.crossfire_auth_service import CrossfireAuthService
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.services.occurrences_service import OccurrencesProcessor

router = APIRouter(prefix="/occurrences", tags=["occurrences"])


def get_auth_service() -> CrossfireAuthService:
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
            detail="Cidade ou estado não encontrados para as coordenadas fornecidas."
        )

    return cidade, estado


async def generate_map(occurrences: list[dict]) -> str:
    """
    Gera um mapa HTML com os pontos de ocorrências.
    - Cluster -1 = verde (ruído)
    - Cluster >= 0 = vermelho (zona perigosa)
    """
    m = folium.Map(location=[-12.9777, -38.5016], zoom_start=12)

    for occ in occurrences:
        lat = occ.get("latitude")
        lon = occ.get("longitude")
        cluster = occ.get("cluster", -1)

        if lat and lon:
            color = "green" if cluster == -1 else "red"
            folium.CircleMarker(
                location=[lat, lon],
                radius=4,
                color=color,
                fill=True,
                fill_opacity=0.6
            ).add_to(m)

    return m._repr_html_()


@router.post("/")
async def get_occurrences(
        location: LocationSchema,
        auth_service: CrossfireAuthService = Depends(get_auth_service),
        occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
        # TODO: Verificar uso futuro do cookie
        access_token: Optional[str] = Cookie(None),
):
    """
    Retorna as ocorrências brutas para a cidade/estado obtidos pela latitude e longitude.
    """
    try:
        city, state = await get_city_and_state(location.latitude, location.longitude)

        access_token = auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API,
            settings.PASSWORD_CROSSFIRE_API
        )
        if not access_token:
            raise ValueError("Não foi possível obter o token de autenticação.")
        occurrence_gateway.set_access_token(access_token)

        today = date.today()
        final_date = today.strftime('%Y-%m-%d')
        initial_date = (today - timedelta(days=90)).strftime('%Y-%m-%d')

        occurrences = await occurrence_gateway.get_occurrences(city_name=city, state_name=state,
                                                               initial_date=initial_date, final_date=final_date)
        print('Número de ocorrências obtidas:', len(occurrences))

        return {"message": "Raw occurrences list", "data": occurrences}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else 503
        detail = (
            f"Erro na API do CrossFire. {exc.response.text}"
            if isinstance(exc, httpx.HTTPStatusError)
            else "Não foi possível conectar à API do CrossFire no momento."
        )
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")


@router.post("/hotspots")
async def analyze_occurrences(
        location: LocationSchema,
        auth_service: CrossfireAuthService = Depends(get_auth_service),
        occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
        access_token: Optional[str] = Cookie(None),
):
    """
    Obtém e analisa hotspots de ocorrências com DBSCAN.
    """
    tempo_inicial = time.perf_counter()

    try:
        cidade, estado = await get_city_and_state(location.latitude, location.longitude)
        print(f"Analisando hotspots de {cidade}/{estado}")

        # --- Redis (opcional, descomentável futuramente) ---
        # redis_client = redis.from_url(
        #     f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
        #     encoding="utf-8", decode_responses=True
        # )
        # analysis_id = f"hotspot_{cidade.lower()}_{estado.lower()}"
        # cached_data = await get_cached_data(redis_client, analysis_id)
        # if cached_data:
        #     print("Dados encontrados no cache Redis.")
        #     return {"message": "Hotspots (cached)", "data": cached_data}

        access_token = auth_service.get_auth_token(
            settings.EMAIL_CROSSFIRE_API,
            settings.PASSWORD_CROSSFIRE_API
        )
        occurrence_gateway.set_access_token(access_token)

        today = date.today()
        final_date = today.strftime('%Y-%m-%d')
        initial_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')

        occurrences = await occurrence_gateway.get_occurrences(city_name=cidade, state_name=estado,
                                                               initial_date=initial_date, final_date=final_date)

        processor = OccurrencesProcessor(epsilon_km=0.7, min_samples=8)
        analyzed_data = processor.cluster_occurrences(occurrences)

        # --- Cache opcional ---
        # await set_cached_data(redis_client, analysis_id, analyzed_data)

        tempo_final = time.perf_counter()
        print(f"Tempo de execução (análise): {tempo_final - tempo_inicial:.4f} segundos")

        return {"message": "List of occurrence hotspots", "data": analyzed_data}

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        status_code = exc.response.status_code if isinstance(exc, httpx.HTTPStatusError) else 503
        detail = (
            f"Erro na API do CrossFire. {exc.response.text}"
            if isinstance(exc, httpx.HTTPStatusError)
            else "Não foi possível conectar à API do CrossFire no momento."
        )
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {str(e)}")


@router.post("/hotspots/map")
async def get_occurrences_map(
        location: LocationSchema,
        auth_service: CrossfireAuthService = Depends(get_auth_service),
        occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
):
    """
    Gera um mapa interativo das ocorrências (teste visual).
    """
    cidade, estado = await get_city_and_state(location.latitude, location.longitude)

    access_token = auth_service.get_auth_token(settings.EMAIL_CROSSFIRE_API, settings.PASSWORD_CROSSFIRE_API)
    occurrence_gateway.set_access_token(access_token)

    today = date.today()
    final_date = today.strftime('%Y-%m-%d')
    initial_date = (today - timedelta(days=365)).strftime('%Y-%m-%d')

    occurrences = await occurrence_gateway.get_occurrences(city_name=cidade, state_name=estado,
                                                           initial_date=initial_date, final_date=final_date)

    processor = OccurrencesProcessor(epsilon_km=0.7, min_samples=8)
    processed = processor.cluster_occurrences(occurrences)

    mapa_html = await generate_map(processed)

    return HTMLResponse(content=mapa_html, status_code=200)
