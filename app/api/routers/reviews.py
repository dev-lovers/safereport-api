from fastapi import APIRouter, Depends
from supabase import Client

from app.domain.reviews.entities.review import Review
from app.domain.reviews.use_cases.create_review_use_case import CreateReviewUseCase
from app.infrastructure.database.repositories.supabase_review_repository import (
    SupabaseReviewRepository,
)
from app.infrastructure.database.supabase_client import get_supabase_client
from app.schemas.response import StandardResponse

router = APIRouter(prefix="/reviews", tags=["Reviews"])


def get_create_review_use_case(
    client: Client = Depends(get_supabase_client),
) -> CreateReviewUseCase:
    repo = SupabaseReviewRepository(client)
    return CreateReviewUseCase(repo)


@router.post("", response_model=StandardResponse)
def create_review(
    review: Review,
    use_case: CreateReviewUseCase = Depends(get_create_review_use_case),
):
    result = use_case.execute(review)
    return StandardResponse(
        message="Avaliação criada com sucesso",
        data=result,
    )
