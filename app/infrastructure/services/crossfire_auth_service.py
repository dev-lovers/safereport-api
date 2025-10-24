
import httpx

AUTH_API_URL = "https://api-service.fogocruzado.org.br/api/v2/auth/login"


class CrossfireAuthService:

    @staticmethod
    def get_auth_token(email: str, password: str) -> str | None:
        """
        Obtém o token de autenticação da API.

        Args:
                    email (str): O email do usuário.
                        password (str): A senha do usuário.

        Raises:
            httpx.HTTPStatusError: Se a API externa retornar um erro (4xx, 5xx).
            httpx.RequestError: Se houver um problema de conexão com a API.
        """
        payload = {"email": email, "password": password}

        try:
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

                if not access_token:
                    raise ValueError(
                        "Token de acesso não encontrado na resposta da API."
                    )

                return access_token

        except httpx.HTTPStatusError as e:
            raise ValueError(f"Falha na autenticação: {e}")
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Erro de rede ao conectar com o serviço de autenticação: {e}"
            )
