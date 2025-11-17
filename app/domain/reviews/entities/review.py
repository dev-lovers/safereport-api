from dataclasses import dataclass
from datetime import datetime


@dataclass
class Ratings:
    map: int
    routes: int
    reportPortal: int


@dataclass
class Review:
    ratings: Ratings
    comment: str
    id: int | None = None
    created_at: datetime | None = None
