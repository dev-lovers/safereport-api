from fastapi import APIRouter, Depends, HTTPException, Query

from app.infrastructure.api_clients.geocode_service import GeocodeService
from app.infrastructure.api_clients.reverse_geocode_service import ReverseGeocodeService

router = APIRouter(prefix="/geocoding", tags=["Geocoding"])


def get_geocode_service() -> GeocodeService:
    return GeocodeService()


def get_reverse_geocode_service() -> ReverseGeocodeService:
    return ReverseGeocodeService()


@router.get("/")
async def geocode_place(
    address: str = Query(..., description="Endereço completo para geocodificação"),
    geocode_service: GeocodeService = Depends(get_geocode_service),
):
    try:
        return geocode_service.get_coordinates(address=address)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/reverse")
async def reverse_geocode_place(
    latitude: float = Query(..., description="Latitude do local"),
    longitude: float = Query(..., description="Longitude do local"),
    reverse_geocode_service: ReverseGeocodeService = Depends(
        get_reverse_geocode_service
    ),
):
    try:
        return reverse_geocode_service.get_address(
            latitude=latitude, longitude=longitude
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
