from abc import ABC, abstractmethod

from app.domain.entities.review import Review


class ReviewRepository(ABC):
    @abstractmethod
    def create(self, review: Review):
        raise NotImplementedError
