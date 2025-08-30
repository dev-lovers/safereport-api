from typing import Optional

import httpx

CROSSFIRE_API_BASE_URL = "https://api-service.fogocruzado.org.br/api/v2"
AUTH_API_URL = "https://api-service.fogocruzado.org.br/api/v2/auth/login"


async def make_request(url: str):
    """
    Get occurrences that occurred in the crossfire API

    Raises:
        httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
        httpx.RequestError: Se houver um problema de conexão com a API.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            timeout=10.0,
        )

        response.raise_for_status()
        return response.json()


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
        print(response_data)
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


def get_occurrences(state_id: str, city_id: str, access_token: str) -> Optional[str]:
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

    # order=ASC&page=1&take=20&idState=813ca36b-91e3-4a18-b408-60b27a1942ef&idCities=d79d2347-bd0d-40aa-8dcc-04134cffd988&idCities=e37f7ad7-cd64-4279-946a-8d689b9b934b
    params = {
        "order": "ASC",
        "page": 1,
        "take": 1,
        "idState": state_id,
        "idCities": city_id,
    }

    with httpx.Client() as client:
        response = client.get(
            f"{CROSSFIRE_API_BASE_URL}/occurrences",
            headers=headers,
            params=params,
            timeout=10.0,
        )

        response.raise_for_status()
        response_data = response.json()

        response_code = response_data.get("code")

        # TODO: Verificar se eu devo retornar None ou uma lista vazia
        if response_code != 200:
            return None

        data_payload = response_data.get("data", [])
        return data_payload
