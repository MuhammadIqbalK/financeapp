import os
from functools import lru_cache

from pydantic_settings import BaseSettings

_BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))


class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 30
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    # Directory containing the built frontend SPA (frontend/build).
    frontend_dir: str = os.path.abspath(os.path.join(_BACKEND_DIR, "..", "frontend", "build"))

    model_config = {
        "env_file": os.path.join(_BACKEND_DIR, ".env"),
        "extra": "ignore",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()
