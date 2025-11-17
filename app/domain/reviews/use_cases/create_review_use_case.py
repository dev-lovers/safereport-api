from app.domain.reviews.entities.review import Review
from app.domain.reviews.interfaces.review_repository import ReviewRepository
from app.schemas.review import ReviewScheme


class CreateReviewUseCase:

    def __init__(self, repo: ReviewRepository):
        self.repo = repo

    def execute(self, review: Review) -> ReviewScheme:
        try:
            new_review = self.repo.create(review)
            return new_review
        except Exception as e:
            raise RuntimeError(f"Erro ao criar avaliação: {e}")
