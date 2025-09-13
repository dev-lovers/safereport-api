import httpx
from fastapi import APIRouter, HTTPException, Request, Depends

from app.core.config import settings
from app.infrastructure.api_clients.autocomplete_service import AutocompleteService
from app.infrastructure.api_clients.geocode_service import GeocodeService
from app.infrastructure.api_clients.reverse_geocode_service import ReverseGeocodeService


router = APIRouter(prefix="/places")


def autocomplete_service() -> AutocompleteService:
    return AutocompleteService()


def geocode_service() -> GeocodeService:
    return GeocodeService()


def reverse_geocode_service() -> ReverseGeocodeService:
    return ReverseGeocodeService()


@router.get("/autocomplete")
async def autocomplete_place(
    query: str,
    # request: Request,
    autocomplete_service: AutocompleteService = Depends(autocomplete_service),
):
    try:
        response = autocomplete_service.get_suggestions(query=query)
        return response

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


@router.post("/geocode")
async def geocode_place(
    address: str,
    # request: Request,
    geocode_service: GeocodeService = Depends(geocode_service),
):
    try:
        response = geocode_service.geocode(address=address)
        return response

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


@router.post("/geocode/reverse")
async def reverse_geocode_place(
    request: Request,
    latitude: float,
    longitude: float,
    reverse_geocode_service: ReverseGeocodeService = Depends(reverse_geocode_service),
):
    try:
        response = reverse_geocode_service.reverse_geocode(
            latitude=latitude, longitude=longitude
        )
        return response

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
