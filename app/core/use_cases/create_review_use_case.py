from app.core.entities.review import Review
from app.core.interfaces.review_repository import ReviewRepository


class CreateReviewUseCase:
    def __init__(self, repository: ReviewRepository):
        self.repository = repository

    def execute(self, ratings, comment):
        review = Review(ratings=ratings, comment=comment)
        return self.repository.create(review)
