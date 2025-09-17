import httpx
import time
import json
import redis
from typing import Optional
from collections import Counter
from fastapi import APIRouter, HTTPException, Response, Depends, Cookie
import requests

from app.core.config import settings
from app.api.schemas.location import LocationSchema

from app.infrastructure.api_clients.crossfire_auth_service import CrossfireAuthService
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.services.hotspot_analysis.sklearn_hotspot_analysis_service import (
    SklearnIHotspotAnalysisService,
)
from app.application.usecases.occurrences.get_occurrence_hotspots import (
    GetOccurrenceHotspotsUseCase,
)

from app.core.config import settings

from app.infrastructure.cache.redis import r


router = APIRouter(prefix="/occurrences", tags=["occurrences"])


def get_auth_service() -> CrossfireAuthService:
    return CrossfireAuthService()


def get_occurrence_gateway() -> CrossfireAPIService:
    return CrossfireAPIService()


def get_analysis_service() -> SklearnIHotspotAnalysisService:
    return SklearnIHotspotAnalysisService()


@router.post("/hotspots")
async def get_occurrence_hotspots(
    location: LocationSchema,
    response: Response,
    auth_service: CrossfireAuthService = Depends(get_auth_service),
    occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
    analysis_service: SklearnIHotspotAnalysisService = Depends(get_analysis_service),
    access_token: Optional[str] = Cookie(None),
):
    """
    Obtém e analisa hotspots de ocorrências.
    """

    tempo_inicial = time.perf_counter()  # Ou time.time()

    #########
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={location.latitude},{location.longitude}&key={settings.GOOGLE_MAPS_API_KEY}"
    response = requests.get(url).json()

    if response["status"] == "OK":
        for component in response["results"][0]["address_components"]:
            if "administrative_area_level_2" in component["types"]:
                cidade = component["long_name"]
            if "administrative_area_level_1" in component["types"]:
                estado = component["long_name"]

    #######

    try:
        analysis_id = f"hotspot_{cidade.lower()}_{estado.lower()}"
        cached_data = r.get(analysis_id)

        if cached_data:
            data = json.loads(cached_data)

            print(
                f"Dados encontrados no Redis para a chave: '{analysis_id}'. Retornando dados salvos."
            )

            # Registra o tempo final
            tempo_final = time.perf_counter()  # Ou time.time()

            # Calcula a diferença e imprime o resultado
            tempo_decorrido = tempo_final - tempo_inicial
            print(f"Tempo de execução: {tempo_decorrido:.4f} segundos")
            return data

    except redis.exceptions.ConnectionError as e:
        print(f"Erro de conexão com o Redis. Prosseguindo com a análise. Erro: {e}")
    except json.JSONDecodeError:
        print(
            f"Erro ao decodificar dados da chave '{analysis_id}'. Prosseguindo com a análise."
        )

    print(
        f"Dados não encontrados no Redis para a chave: '{analysis_id}'. Iniciando análise..."
    )

    try:
        use_case = GetOccurrenceHotspotsUseCase(
            auth_service=auth_service,
            occurrence_gateway=occurrence_gateway,
            analysis_service=analysis_service,
        )

        analyzed_data = use_case.execute(
            email=settings.EMAIL_CROSSFIRE_API,
            password=settings.PASSWORD_CROSSFIRE_API,
            city_name=cidade,
            state_name=estado,
        )

        #

        # Registra o tempo final
        tempo_final = time.perf_counter()  # Ou time.time()

        # Calcula a diferença e imprime o resultado
        tempo_decorrido = tempo_final - tempo_inicial
        print(f"Tempo de execução: {tempo_decorrido:.4f} segundos")

        # 3. Salva os dados no Redis para uso futuro
        try:
            data_to_save = json.dumps(analyzed_data)
            r.set(analysis_id, data_to_save)
            print(f"Análise concluída e salva no Redis com a chave: '{analysis_id}'")
        except Exception as e:
            print(f"Erro ao salvar dados no Redis: {e}")

        return {"message": "List of occurrence hotspots", "data": analyzed_data}

        # cluster_counts = Counter(occ["cluster"] for occ in analyzed_data)
        # print("Cluster counts:", dict(cluster_counts))

        # return {"message": "List of occurrence hotspots", "data": analyzed_data}

    except ValueError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e),
        )
    except (httpx.HTTPStatusError, httpx.RequestError) as exc:
        if isinstance(exc, httpx.HTTPStatusError):
            status_code = exc.response.status_code
            detail = f"Erro na API do CrossFire. {exc.response.text}"
        else:
            status_code = 503
            detail = "Não foi possível conectar à API do CrossFire no momento."
        raise HTTPException(status_code=status_code, detail=detail)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ocorreu um erro inesperado: {str(e)}",
        )
