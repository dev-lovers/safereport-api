import httpx
from typing import Optional
from collections import Counter
from fastapi import APIRouter, HTTPException, Response, Depends, Cookie

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
    try:
        use_case = GetOccurrenceHotspotsUseCase(
            auth_service=auth_service,
            occurrence_gateway=occurrence_gateway,
            analysis_service=analysis_service,
        )

        analyzed_data = use_case.execute(
            email=settings.EMAIL_CROSSFIRE_API,
            password=settings.PASSWORD_CROSSFIRE_API,
            city_name=location.city_name,
            state_name=location.state_name,
        )

        cluster_counts = Counter(occ["cluster"] for occ in analyzed_data)
        print("Cluster counts:", dict(cluster_counts))

        return {"message": "List of occurrence hotspots", "data": analyzed_data}

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
