import httpx

CROSSFIRE_API_URL = "https://jsonplaceholder.typicode.com"


async def fetch_incidents():
    """
    Get incidents that occurred in the crossfire API

    Raises:
        httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
        httpx.RequestError: Se houver um problema de conexão com a API.
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{CROSSFIRE_API_URL}/todos/1/",
            timeout=10.0,
        )

        response.raise_for_status()
        return response.json()
