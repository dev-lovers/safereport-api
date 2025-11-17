import httpx
from fastapi import APIRouter, Depends, HTTPException, status

from app.domain.occurrences.use_cases.get_hotspots_use_case import (
    GetHotspotsUseCase,
)
from app.domain.occurrences.use_cases.get_occurrences_use_case import (
    GetOccurrencesUseCase,
)
from app.infrastructure.api_clients.crossfire_client import CrossfireAPIService
from app.infrastructure.auth.crossfire_auth_service import CrossfireAuthService
from app.infrastructure.cache.redis_cache_service import RedisClient, get_redis_client
from app.schemas.coordinates import CoordinateScheme
from app.schemas.response import StandardResponse

router = APIRouter(prefix="/occurrences", tags=["Occurrences"])


def get_crossfire_auth_service() -> CrossfireAuthService:
    return CrossfireAuthService()


def get_occurrence_gateway() -> CrossfireAPIService:
    return CrossfireAPIService()


def get_occurrences_use_case(
    auth_service: CrossfireAuthService = Depends(get_crossfire_auth_service),
    occurrence_gateway: CrossfireAPIService = Depends(get_occurrence_gateway),
    redis_client: RedisClient = Depends(get_redis_client),
) -> GetOccurrencesUseCase:
    return GetOccurrencesUseCase(
        auth_service=auth_service,
        occurrence_gateway=occurrence_gateway,
        redis_client=redis_client,
    )


def get_hotspots_use_case(
    redis_client: RedisClient = Depends(get_redis_client),
) -> GetHotspotsUseCase:
    return GetHotspotsUseCase(redis_client=redis_client)


@router.get("", response_model=StandardResponse[list[dict]])
async def get_occurrences(
    coordinates: CoordinateScheme = Depends(),
    use_case: GetOccurrencesUseCase = Depends(get_occurrences_use_case),
):
    """
    Retorna as ocorrências brutas para a cidade/estado obtidos pela latitude e longitude.
    """
    try:
        occurrences = await use_case.execute(coordinates)

        return StandardResponse[list[dict]](
            message="Lista bruta de ocorrências",
            data=occurrences,
        )

    except HTTPException:
        # Re-levanta HTTPException para o FastAPI tratar diretamente
        raise
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
            status_code=500,
            detail=f"Ocorreu um erro inesperado: {str(e)}",
        )


@router.get("/hotspots", response_model=StandardResponse[list[dict]])
async def get_hotspots(
    use_case: GetHotspotsUseCase = Depends(get_hotspots_use_case),
):
    """
    Obtém a análise de hotspots de ocorrências mais recente.

    Estes dados são pré-processados por um worker em segundo plano
    e armazenados em cache para entrega imediata.
    """
    try:
        analysis_data_dict = use_case.execute()

        return StandardResponse[list[dict]](
            message="Análise de hotspots obtida com sucesso",
            data=analysis_data_dict,
        )

    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ocorreu um erro inesperado no servidor.",
        )
