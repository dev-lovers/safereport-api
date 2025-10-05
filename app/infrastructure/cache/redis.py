import redis

from app.core.config import settings


class Redis:
    def __init__(self):
        # Usando as variáveis de ambiente para configurar a conexão com o Redis
        self.r = redis.Redis(
            host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
        )

    def set(self, key, value):
        self.r.set(key, value)

    def get(self, key):
        return self.r.get(key)


r = Redis()

# async def get_cached_data(redis_client: redis.Redis, key: str) -> Optional[dict]:
#     """
#     Obtém dados do Redis, se existirem.
#     """
#     try:
#         cached = await redis_client.get(key)
#         if cached:
#             return json.loads(cached)
#     except (redis.exceptions.RedisError, json.JSONDecodeError) as e:
#         print(f"Erro ao acessar cache Redis: {e}")
#     return None
#
#
# async def set_cached_data(redis_client: redis.Redis, key: str, data: dict, expire: int = 3600):
#     """
#     Salva dados no Redis com tempo de expiração.
#     """
#     try:
#         await redis_client.set(key, json.dumps(data), ex=expire)
#     except redis.exceptions.RedisError as e:
#         print(f"Erro ao salvar dados no Redis: {e}")
