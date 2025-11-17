import json

from app.infrastructure.cache.redis_cache_service import RedisClient
from fastapi import HTTPException, status

CACHE_KEY = "analysis_result_salvador"


class GetHotspotsUseCase:
    """
    Use case responsável por buscar do cache a análise de hotspots
    já pré-processada por um worker em background.
    """

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis_client = redis_client

    def execute(self) -> list[dict]:
        if not self.redis_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço de cache indisponível.",
            )

        cached_data_str = self.redis_client.get_data(CACHE_KEY)

        if cached_data_str is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    "Nenhum resultado de análise encontrado. "
                    "O processamento inicial pode estar em andamento."
                ),
            )

        try:
            analysis_data_dict = json.loads(cached_data_str)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar dados do cache. Formato inválido.",
            )

        return analysis_data_dict
