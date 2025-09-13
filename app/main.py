from fastapi import FastAPI

from app.core.config import settings
from app.api.routers import occurrences, places


app = FastAPI(title=settings.PROJECT_NAME)


app.include_router(occurrences.router)
app.include_router(places.router)
