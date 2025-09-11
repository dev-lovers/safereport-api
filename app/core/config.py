from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SafeReport API"
    API_V1_STR: str = "/api/v1"
    EMAIL_CROSSFIRE_API: str
    PASSWORD_CROSSFIRE_API: str
    GOOGLE_MAPS_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
