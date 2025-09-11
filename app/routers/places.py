import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.utils import validate_coordinates


router = APIRouter(prefix="/places")
client = httpx.AsyncClient()


@router.get("/autocomplete")
async def autocomplete_place(query: str, request: Request):
    try:
        if not query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")

        client: httpx.AsyncClient = request.app.state.client
        response = await client.post(
            "https://places.googleapis.com/v1/places:searchText",
            json={"textQuery": query},
            headers={
                "Content-Type": "application/json",
                "X-Goog-Api-Key": settings.GOOGLE_MAPS_API_KEY,
                "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.priceLevel",
            },
        )
        response.raise_for_status()
        return response.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erro ao chamar Google Maps API: {e.response.text}",
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Falha ao se conectar à Google Maps API: {str(e)}",
        )
    except Exception as e:
        HTTPException(status_code=500, detail="Erro interno no servidor")
