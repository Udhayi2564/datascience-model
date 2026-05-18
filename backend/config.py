from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    GEMINI_API_KEY: str = ""
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    ALLOWED_ORIGINS: str = "http://localhost:3000"
    DATA_DIR: str = "/app/data"
    MODELS_DIR: str = "/app/models"

    class Config:
        env_file = ".env"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
