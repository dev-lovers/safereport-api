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
