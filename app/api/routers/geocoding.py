from fastapi import APIRouter, Depends, Query

from app.domain.geocoding.use_cases.get_address_use_case import (
    GetAddressUseCase,
)
from app.domain.geocoding.use_cases.get_coordinates_use_case import (
    GetCoordinatesUseCase,
)
from app.infrastructure.api_clients.google_geocode_client import GeocodeService
from app.infrastructure.api_clients.google_reverse_geocode_client import (
    ReverseGeocodeService,
)
from app.schemas.response import StandardResponse

router = APIRouter(prefix="/geocoding", tags=["Geocoding"])


def get_coordinates_use_case() -> GetCoordinatesUseCase:
    return GetCoordinatesUseCase(GeocodeService())


def get_reverse_geocode_use_case() -> GetAddressUseCase:
    return GetAddressUseCase(ReverseGeocodeService())


@router.get("", response_model=StandardResponse)
async def geocode_place(
    address: str = Query(..., description="Endereço completo para geocodificação"),
    use_case: GetCoordinatesUseCase = Depends(get_coordinates_use_case),
):
    result = await use_case.execute(address)
    return StandardResponse(message="Geocodificação realizada com sucesso", data=result)


@router.get("/reverse", response_model=StandardResponse)
async def reverse_geocode_place(
    latitude: float = Query(...),
    longitude: float = Query(...),
    use_case: GetAddressUseCase = Depends(get_reverse_geocode_use_case),
):
    result = await use_case.execute(latitude, longitude)
    return StandardResponse(
        message="Geocodificação reversa realizada com sucesso", data=result
    )
