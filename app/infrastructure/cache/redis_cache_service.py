import json
from typing import Any

import redis

# Assumindo que 'app.core.config.settings' é um módulo acessível com as configurações
from app.config import settings


class RedisClient:
    """
    Cliente para gerir a conexão e as operações síncronas com o Redis.
    Encapsula as funcionalidades básicas (set, get) e a lógica de cache (JSON).
    """

    def __init__(self):
        """
        Inicializa o cliente Redis e estabelece a conexão.
        """
        try:
            self.r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
            )
            self.r.ping()
            print("Conexão com Redis estabelecida com sucesso!")
        except redis.exceptions.ConnectionError as e:
            print(
                f"ERRO: Não foi possível conectar ao Redis. Verifique as configurações. Detalhes: {e}"
            )
            self.r = None

    def set_data(self, key: str, value: Any, expire: int | None = None) -> bool:
        """
        Salva dados (string, número, etc.) no Redis.

        :param key: A chave para guardar os dados.
        :param value: O valor a ser guardado.
        :param expire: Tempo de expiração em segundos (opcional).
        :return: True se a operação for bem-sucedida, False caso contrário.
        """
        if not self.r:
            return False
        try:
            # O 'set' da biblioteca redis-py é síncrono
            self.r.set(key, value, ex=expire)
            return True
        except redis.exceptions.RedisError as e:
            print(f"Erro ao salvar dados no Redis para a chave '{key}': {e}")
            return False

    def get_data(self, key: str) -> str | None:
        """
        Obtém dados guardados no Redis.

        :param key: A chave para obter os dados.
        :return: O valor como string, ou None se a chave não existir ou em caso de erro.
        """
        if not self.r:
            return None
        try:
            # O 'get' da biblioteca redis-py é síncrono
            return self.r.get(key)
        except redis.exceptions.RedisError as e:
            print(f"Erro ao obter dados do Redis para a chave '{key}': {e}")
            return None

    # --- Lógica de Cache (JSON) para Estruturas Mais Complexas ---

    def get_json_cache(self, key: str) -> dict[str, Any] | None:
        """
        Obtém e desserializa dados JSON do Redis.

        :param key: A chave do cache.
        :return: Um dicionário (dict) se o cache existir e for válido, ou None.
        """
        cached_str = self.get_data(key)  # Reutiliza o método síncrono 'get_data'
        if cached_str is None:
            return None

        try:
            # 2. Boa Prática: Tratamento de erro na desserialização JSON
            return json.loads(cached_str)
        except json.JSONDecodeError as e:
            print(
                f"Erro ao desserializar JSON para a chave '{key}': {e}. Valor: {cached_str}"
            )
            return None

    def set_json_cache(
        self, key: str, data: dict[str, Any], expire: int = 3600
    ) -> bool:
        """
        Serializa e salva um dicionário (dict) como JSON no Redis.

        :param key: A chave do cache.
        :param data: O dicionário de dados a ser guardado.
        :param expire: Tempo de expiração em segundos (padrão: 3600s = 1 hora).
        :return: True se a operação for bem-sucedida, False caso contrário.
        """
        try:
            # 3. Boa Prática: Serialização para JSON antes de salvar
            json_data = json.dumps(data)
            return self.set_data(
                key, json_data, expire=expire
            )  # Reutiliza o método síncrono 'set_data'
        except TypeError as e:
            # Tratamento de erro caso o objeto não seja serializável
            print(f"Erro ao serializar dados para JSON para a chave '{key}': {e}")
            return False


# Variável global para armazenar a única instância do cliente Redis
_redis_client_instance = None


def get_redis_client() -> RedisClient:
    """
    Função de dependência do FastAPI para fornecer uma única instância (Singleton)
    do RedisClient síncrono.
    """
    global _redis_client_instance

    # Se a instância ainda não foi criada, crie-a
    if _redis_client_instance is None:
        _redis_client_instance = RedisClient()

    # Verifica se a conexão falhou durante a inicialização
    if _redis_client_instance.r is None:
        # Lança uma exceção para o FastAPI tratar (o que impede a rota de continuar)
        raise ConnectionRefusedError("A conexão com o Redis não foi estabelecida.")

    return _redis_client_instance
