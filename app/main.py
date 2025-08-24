from fastapi import FastAPI

from app.routers import incidents
from app.core.config import settings


app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(incidents.router)


@app.get("/")
def read_root():
    return {"message": f"Bem-vindo à {settings.PROJECT_NAME}"}
