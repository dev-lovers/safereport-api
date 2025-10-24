from fastapi import FastAPI

from app.api.routers import autocomplete, geocoding, occurrences, reviews
from app.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(occurrences.router)
app.include_router(autocomplete.router)
app.include_router(geocoding.router)
app.include_router(reviews.router)
