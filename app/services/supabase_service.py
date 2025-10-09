from supabase import create_client, Client
from app.core.config import settings
from typing import Optional

_supabase_client: Optional[Client] = None


class SupabaseClientError(Exception):
    """Exceção para erros na inicialização do cliente Supabase."""

    pass


def get_supabase_client() -> Client:
    """
    Inicializa o cliente Supabase se ainda não foi inicializado (Singleton)
    e devolve a instância.
    """
    global _supabase_client

    if _supabase_client is None:
        url: str = settings.SUPABASE_URL
        key: str = settings.SUPABASE_KEY

        if not url or not key:
            raise SupabaseClientError(
                "As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas ou estão vazias."
            )

        _supabase_client = create_client(url, key)

    return _supabase_client
