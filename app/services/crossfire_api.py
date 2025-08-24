import httpx

CROSSFIRE_API_URL = ""
AUTH_API_URL = "https://api-service.fogocruzado.org.br/api/v2/auth/login"


async def make_request(url: str):
    """
    Get incidents that occurred in the crossfire API

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
        data_payload = response_data.get("data", {})
        access_token = data_payload.get("accessToken", "")

        return access_token
