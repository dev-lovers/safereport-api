import httpx
from typing import Optional

from fastapi import APIRouter, HTTPException, Response, Cookie

from app.core.config import settings
from app.services import crossfire_api

router = APIRouter(prefix="/incidents")

from pydantic import BaseModel


class LocationSchema(BaseModel):
    country: str
    state: str
    city: str
    street: Optional[str] = None
    neighborhood: Optional[str] = None


@router.post("/hotspots")
async def get_incident_hotspots(
    location: LocationSchema,
    response: Response,
    access_token: Optional[str] = Cookie(None),
):
    """
    Get and analyze incident hotspots based on data from one or more APIs.

    Returns:
      List[Incident]: List of incident hotspots.
    """
    try:
        if access_token is None:
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

        state_id = crossfire_api.get_state_id(location.state, access_token)

        if state_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"Estado '{location.state}' não encontrado na API do CrossFire.",
            )

        # TODO: No endpoint da cidade, fornece o ID do estado. Verificar se não é mais interessante usar apenas esse endpoint para buscar ambas as infromações.
        city_id = crossfire_api.get_city_id(location.city, access_token)

        if city_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"Cidade '{location.city}' não encontrado na API do CrossFire.",
            )

        # TODO: Incidente ou Ocorrência? Verificar o termo mais adequado. Ocorrência está ganhando por enquanto.
        occurrences = crossfire_api.get_occurrences(
            state_id=state_id, city_id=city_id, access_token=access_token
        )
        print(occurrences)

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

    return {"message": "List of incident hotspots"}
