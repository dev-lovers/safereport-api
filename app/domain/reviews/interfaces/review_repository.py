from abc import ABC, abstractmethod

from app.domain.reviews.entities.review import Review


class ReviewRepository(ABC):

    @abstractmethod
    async def create(self, review: Review) -> Review:
        pass
