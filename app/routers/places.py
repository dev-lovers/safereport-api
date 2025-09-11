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


@router.post("/geocode")
async def geocode_place(address: str, request: Request):
    try:
        if not address:
            raise HTTPException(status_code=400, detail="Endereço é obrigatório")

        client: httpx.AsyncClient = request.app.state.client
        response = await client.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": address, "key": settings.GOOGLE_MAPS_API_KEY},
        )

        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            response = data["results"][0]["geometry"]["location"]
            lat = response["lat"]
            lng = response["lng"]
            return {"latitude": lat, "longitude": lng}
        else:
            raise HTTPException(status_code=404, detail="Endereço não encontrado")

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


@router.post("/geocode/reverse")
async def geocode_reverse_place(latitude: float, longitude: float, request: Request):
    try:
        if not latitude and not longitude:
            raise HTTPException(
                status_code=400, detail="Latitude e Longitude são obrigatórias"
            )

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
