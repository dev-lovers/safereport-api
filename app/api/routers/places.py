from fastapi import APIRouter, HTTPException, Depends, Query

from app.infrastructure.api_clients.autocomplete_service import AutocompleteService
from app.infrastructure.api_clients.geocode_service import GeocodeService
from app.infrastructure.api_clients.reverse_geocode_service import ReverseGeocodeService

from app.api.schemas.places import (
    GeocodeRequest,
    ReverseGeocodeRequest,
    GeocodeResponse,
    ReverseGeocodeResponse,
)

router = APIRouter(prefix="/places", tags=["Places"])


def get_autocomplete_service() -> AutocompleteService:
    return AutocompleteService()


def get_geocode_service() -> GeocodeService:
    return GeocodeService()


def get_reverse_geocode_service() -> ReverseGeocodeService:
    return ReverseGeocodeService()


@router.get("/autocomplete")
async def autocomplete_place(
    query: str = Query(..., description="Termo de busca para sugestões de lugares"),
    autocomplete_service: AutocompleteService = Depends(get_autocomplete_service),
):
    try:
        return autocomplete_service.get_suggestions(query=query)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geocode")
async def geocode_place(
    payload: GeocodeRequest,
    geocode_service: GeocodeService = Depends(get_geocode_service),
):
    try:
        return geocode_service.geocode(address=payload.address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/geocode/reverse")
async def reverse_geocode_place(
    payload: ReverseGeocodeRequest,
    reverse_geocode_service: ReverseGeocodeService = Depends(
        get_reverse_geocode_service
    ),
):
    try:
        return reverse_geocode_service.reverse_geocode(
            latitude=payload.latitude, longitude=payload.longitude
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
