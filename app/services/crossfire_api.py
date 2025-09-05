from typing import Optional, List

import httpx
from fastapi import HTTPException

from app.schemas.location import LocationSchema


CROSSFIRE_API_BASE_URL = "https://api-service.fogocruzado.org.br/api/v2"
AUTH_API_URL = "https://api-service.fogocruzado.org.br/api/v2/auth/login"


def get_auth_token(email, password):
    """
    Get auth token from the auth API

    Raises:
        httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
        httpx.RequestError: Se houver um problema de conexão com a API.
    """
    payload = {"email": email, "password": password}

    with httpx.Client() as client:
        response = client.post(
            AUTH_API_URL,
            json=payload,
            timeout=10.0,
        )

        response.raise_for_status()
        response_data = response.json()

        data_payload = response_data.get("data", {})
        access_token = data_payload.get("accessToken", "")

        return access_token


def get_state_id(state: str, access_token: str) -> Optional[str]:
    # TODO: Ajustar docstring
    """
    Get auth token from the auth API

    Raises:
        httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
        httpx.RequestError: Se houver um problema de conexão com a API.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    with httpx.Client() as client:
        response = client.get(
            f"{CROSSFIRE_API_BASE_URL}/states",
            headers=headers,
            timeout=10.0,
        )

        response.raise_for_status()
        response_data = response.json()
        data_payload = response_data.get("data", [])

        for state_info in data_payload:
            state_name = state_info.get("name").lower()
            if state_name == state.lower():
                return state_info.get("id")

        return None


def get_city_id(city: str, access_token: str) -> Optional[str]:
    # TODO: Ajustar docstring
    """
    Get auth token from the auth API

    Raises:
        httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
        httpx.RequestError: Se houver um problema de conexão com a API.
    """
    city = city.upper()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    params = {"cityName": city}

    with httpx.Client() as client:
        response = client.get(
            f"{CROSSFIRE_API_BASE_URL}/cities",
            headers=headers,
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()
        response_data = response.json()
        data_payload = response_data.get("data", [])

        for city_info in data_payload:
            city_name = city_info.get("name")
            if city_name == city:
                return city_info.get("id")

        return None


def get_location_ids(location: LocationSchema, token: str):
    state_id = get_state_id(location.state, token)
    if not state_id:
        raise HTTPException(
            status_code=404, detail=f"Estado '{location.state}' não encontrado."
        )

    city_id = get_city_id(location.city, token)
    if not city_id:
        raise HTTPException(
            status_code=404, detail=f"Cidade '{location.city}' não encontrada."
        )

    return state_id, city_id


def get_occurrences(
    state_id: str, city_id: str, access_token: str
) -> Optional[List[dict]]:
    """
    Busca todas as ocorrências paginadas da API externa.

    Args:
        state_id (str): ID do estado.
        city_id (str): ID da cidade.
        access_token (str): Token de autenticação.

    Returns:
        list[dict] | None: Lista com todas as ocorrências, ou None se houver erro.
    """
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    with httpx.Client() as client:
        params = {
            "order": "ASC",
            "initialdate": "2025-07-04",
            "finaldate": "2025-08-04",
            "idState": state_id,
            "idCities": city_id,
        }

        response = client.get(
            f"{CROSSFIRE_API_BASE_URL}/occurrences",
            headers=headers,
            params=params,
            timeout=10.0,
        )
        response.raise_for_status()
        response_data = response.json()

        response_code = response_data.get("code")
        if response_code != 200:
            return None

        occurrences = response_data.get("data", [])

    return occurrences
