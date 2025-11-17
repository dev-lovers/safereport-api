from typing import Any

from app.domain.reviews.entities.review import Ratings, Review
from app.domain.reviews.interfaces.review_repository import ReviewRepository
from supabase import Client


class RepositoryError(Exception):
    """Exceção base para erros de persistência no repositório."""

    pass


class SupabaseReviewRepository(ReviewRepository):
    """
    Implementação do Repositório para PostgreSQL/Supabase.
    """

    def __init__(self, client: Client):
        self.client = client
        self.table_name = "reviews"

    def _to_db_format(self, review: Review) -> dict[str, Any]:
        """Converte a Entidade Review em um dicionário para inserção no DB."""

        ratings_json = {
            "map": review.ratings.map,
            "routes": review.ratings.routes,
            "reportPortal": review.ratings.reportPortal,
        }

        return {
            "ratings": ratings_json,
            "comment": review.comment,
        }

    def _to_entity(self, db_row: dict[str, Any]) -> Review:
        """Converte a linha (row) do DB em uma Entidade Review."""

        # Mapeamento do sub-objeto Ratings (se for armazenado como JSONB)
        ratings_data = db_row["ratings"]
        ratings_entity = Ratings(
            map=ratings_data["map"],
            routes=ratings_data["routes"],
            reportPortal=ratings_data["reportPortal"],
        )

        return Review(
            id=db_row["id"],
            ratings=ratings_entity,
            comment=db_row["comment"],
            created_at=db_row["created_at"],
        )

    def create(self, review: Review) -> Review:
        """
        Insere uma nova review no Supabase e devolve a entidade completa.
        """
        try:
            db_data = self._to_db_format(review)

            response = self.client.table(self.table_name).insert(db_data).execute()

            data: list[dict[str, Any]] = response.data

            if not data:
                raise RepositoryError("A inserção retornou um resultado vazio.")

            return self._to_entity(data[0])

        except RepositoryError as e:
            raise e
        except Exception as e:
            raise RepositoryError(f"Falha ao criar review no Supabase: {e}")
