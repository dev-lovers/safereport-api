import httpx
from fastapi import FastAPI

from app.core.config import settings
from app.routers import occurrences, places


app = FastAPI(title=settings.PROJECT_NAME)


@app.on_event("startup")
async def startup_event() -> None:
    app.state.client = httpx.AsyncClient(timeout=10.0)


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await app.state.client.aclose()


app.include_router(occurrences.router)
app.include_router(places.router)
