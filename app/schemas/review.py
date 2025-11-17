from dataclasses import asdict
from datetime import datetime

from pydantic import BaseModel

from app.domain.reviews.entities.review import Review as ReviewEntity


class Ratings(BaseModel):
    map: int
    routes: int
    reportPortal: int


class ReviewScheme(BaseModel):
    ratings: Ratings
    comment: str
    id: int | None = None
    created_at: datetime | None = None

    @classmethod
    def from_entity(cls, entity: ReviewEntity):
        return cls(**asdict(entity))
