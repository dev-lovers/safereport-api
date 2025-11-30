from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Dict
import json


class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeReport API"
    API_V1_STR: str = "/api/v1"

    EMAIL_CROSSFIRE_API: str
    PASSWORD_CROSSFIRE_API: str
    GOOGLE_MAPS_API_KEY: str

    SUPABASE_URL: str
    SUPABASE_KEY: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    CITIES_TO_PROCESS: List[Dict] = Field(
        default=[
            {"city": "Salvador", "state": "Bahia", "days_ago": 365},
            {"city": "Belém", "state": "Pará", "days_ago": 365},
            {"city": "Rio de Janeiro", "state": "Rio de Janeiro", "days_ago": 365},
            {"city": "Recife", "state": "Pernambuco", "days_ago": 365},
        ]
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        json_loads=json.loads,
    )


settings = Settings()
