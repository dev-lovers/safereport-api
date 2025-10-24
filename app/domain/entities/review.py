from dataclasses import dataclass
from datetime import datetime

# TODO: Adicionar validação do número de estrelas (1 a 5)
# class QualityLevels(Enum):
#     PÉSSIMO = 1
#     INSUFICIENTE = 2
#     RAZOÁVEL = 3
#     BOM = 4
#     EXCELENTE = 5


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
