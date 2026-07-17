from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, computed_field
from typing import List, Union


class Settings(BaseSettings):
    PROJECT_NAME: str = "AEGON Enterprise Platform"
    VERSION: str = "5.0.0"
    API_V1_STR: str = "/api/v1"

    # CORS
    BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
    ]
    # Allow passing additional CORS origins dynamically in production
    FRONTEND_URLS: str = ""

    @computed_field
    @property
    def cors_origins(self) -> List[str]:
        origins = [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS]
        if self.FRONTEND_URLS:
            origins.extend([url.strip().rstrip("/") for url in self.FRONTEND_URLS.split(",") if url.strip()])
        return list(set(origins))

    # SUPABASE
    SUPABASE_URL: str
    SUPABASE_SECRET_KEY: str
    SUPABASE_JWKS_URL: str

    # DATABASE
    DATABASE_URL: str

    # REDIS
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    @computed_field
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # RABBITMQ / CELERY
    RABBITMQ_HOST: str = "localhost"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASSWORD: str = "guest"

    @computed_field
    @property
    def CELERY_BROKER_URL(self) -> str:
        return (
            f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}"
            f"@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"
        )

    # AUTHENTICATION
    # Production authentication uses Supabase Auth (RS256 JWT via JWKS).
    # See SUPABASE_JWKS_URL above and backend/app/core/security.py.

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
