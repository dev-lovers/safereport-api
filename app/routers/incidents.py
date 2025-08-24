import httpx
from typing import List

from fastapi import APIRouter, HTTPException

from app.services import crossfire_api

router = APIRouter(prefix="/incidents")


@router.get("/hotspots")
async def get_incident_hotspots():
    """
    Get and analyze incident hotspots based on data from one or more APIs.

    Returns:
      List[Incident]: List of incident hotspots.
    """
    try:
        data = await crossfire_api.fetch_incidents()
        print(data)
        # return data

    except httpx.HTTPStatusError as exc:
        # Se o erro foi um status HTTP (ex: 404 Not Found),
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=f"Erro na API do CrossFire",
        )
    except httpx.RequestError:
        # Se o erro foi de conexão, retornamos um erro 503 Service Unavailable.
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar à API do CrossFire no momento.",
        )

    return {"message": "List of incident hotspots"}
