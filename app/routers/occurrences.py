import httpx
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Cookie

from app.core.config import settings
from app.services import crossfire_api
from app.services import hotspot_service
from app.schemas.location import LocationSchema
from collections import Counter

router = APIRouter(prefix="/occurrences")


@router.post("/hotspots")
async def get_occurrence_hotspots(
    location: LocationSchema,
    response: Response,
    access_token: Optional[str] = Cookie(None),
):
    """
    Get and analyze occurrence hotspots based on data from one or more APIs.

    Returns:
      List[Occurrence]: List of Occurrence hotspots.
    """
    try:
        if True:
            email = settings.EMAIL_CROSSFIRE_API
            password = settings.PASSWORD_CROSSFIRE_API

            access_token = crossfire_api.get_auth_token(email, password)

            if access_token == "":
                raise HTTPException(
                    status_code=401,
                    detail="Não foi possível obter o token de autenticação.",
                )

            response.set_cookie(
                key="access_token",
                value=access_token,
                httponly=True,
                secure=True,
                samesite="strict",
                max_age=60 * 60 * 24,
            )

        state_id, city_id = crossfire_api.get_location_ids(location, access_token)
        occurrences = crossfire_api.get_occurrences(
            state_id=state_id, city_id=city_id, access_token=access_token
        )

        occurrences_formatted = [
            {
                "id": occurrence.get("id"),
                "latitude": occurrence.get("latitude"),
                "longitude": occurrence.get("longitude"),
                "type_crime": occurrence.get("contextInfo", {})
                .get("mainReason", {})
                .get("name", ""),
            }
            for occurrence in occurrences
        ]

        analyzed_data = hotspot_service.analyze_occurrences(occurrences_formatted)

        cluster_counts = Counter(occ["cluster"] for occ in analyzed_data)
        cluster_counts = dict(cluster_counts)
        print("Cluster counts:", cluster_counts)

    except httpx.HTTPStatusError as exc:
        # Se o erro foi um status HTTP (ex: 404 Not Found),
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Erro na API do CrossFire. {exc.response.text}",
        )
    except httpx.RequestError:
        # Se o erro foi de conexão, retornamos um erro 503 Service Unavailable.
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar à API do CrossFire no momento.",
        )

    return {"message": "List of occurrence hotspots"}
