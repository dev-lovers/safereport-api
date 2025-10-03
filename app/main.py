from fastapi import FastAPI

from app.api.routers import occurrences, geocoding, autocomplete
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(occurrences.router)
app.include_router(autocomplete.router)
app.include_router(geocoding.router)
