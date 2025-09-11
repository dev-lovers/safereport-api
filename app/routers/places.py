import httpx
from fastapi import APIRouter, HTTPException, Request

from app.core.config import settings
from app.utils import validate_coordinates


router = APIRouter(prefix="/places")


@router.get("/autocomplete")
async def autocomplete_place(query: str, request: Request):
    try:
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


@router.post("/geocode")
async def geocode_place(address: str, request: Request):
    try:
        client: httpx.AsyncClient = request.app.state.client
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": settings.GOOGLE_MAPS_API_KEY},
        )

        response.raise_for_status()
        data = response.json()

        if data["status"] == "ZERO_RESULTS" and not data["results"]:
            raise HTTPException(
                status_code=404, detail="Não foi possível decodificar o endereço"
            )

        coords = data["results"][0]["geometry"]["location"]
        lat = coords["lat"]
        lng = coords["lng"]
        return {"latitude": lat, "longitude": lng}

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
async def geocode_reverse_place(latitude: float, longitude: float, request: Request):
    try:
        # TODO: A forma como eu estou chamando a função deve ser melhorada
        is_coordinates_valid = validate_coordinates.validate_coordinates(
            latitude, longitude
        )

        if is_coordinates_valid is False:
            raise HTTPException(
                status_code=400, detail="Latitude ou Longitude inválidas"
            )

        client: httpx.AsyncClient = request.app.state.client
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={
                "latlng": f"{latitude}, {longitude}",
                "key": settings.GOOGLE_MAPS_API_KEY,
            },
        )

        response.raise_for_status()
        data = response.json()

        if data["status"] == "ZERO_RESULTS" and not data["results"]:
            raise HTTPException(
                status_code=404,
                detail="Não foi encontrado um endereço para as coordenadas fornecidas",
            )

        return {"address": data["results"][0]["formatted_address"]}

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
