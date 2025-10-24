from fastapi import APIRouter, Depends, HTTPException
from supabase import Client

from app.domain.entities.review import Review
from app.infrastructure.persistence.supabase_review_repository import (
    RepositoryError,
    SupabaseReviewRepository,
)
from app.services.supabase_service import (
    get_supabase_client,
)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_review_repository(
    client: Client = Depends(get_supabase_client),
) -> SupabaseReviewRepository:
    """
    Dependência que fornece uma instância do SupabaseReviewRepository.
    O 'client' é injetado usando a dependência 'get_supabase_client'.
    """
    return SupabaseReviewRepository(client=client)


@router.post("/")
async def create_review(
    review: Review,
    repository: SupabaseReviewRepository = Depends(get_review_repository),
):
    try:
        created_review = repository.create(review)
        return {"message": "Review created successfully", "review": created_review}

    except RepositoryError as e:
        raise HTTPException(status_code=500, detail=f"Erro de persistência: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ocorreu um erro inesperado: {e}")
