from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env.development", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    environment: str = "development"

    database_url: str = "postgresql+asyncpg://culinary:culinary@localhost:5432/culinary_blog"

    cache_redis_url: str = "redis://localhost:6380/0"
    queue_redis_url: str = "redis://localhost:6381/0"
    ratelimit_redis_url: str = "redis://localhost:6382/0"

    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "culinary-blog"
    minio_secure: bool = False

    otel_exporter_otlp_endpoint: str = "http://localhost:4317"
    otel_service_name: str = "culinary-blog-api"

    cors_origins: str = "http://localhost:3000"

    jwt_secret_key: str = "dev-only-insecure-secret-change-me"
    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 7
    cookie_secure: bool = True
    max_failed_logins: int = 5
    lockout_minutes: int = 15

    @model_validator(mode="after")
    def _require_real_secret_outside_development(self) -> "Settings":
        if self.environment != "development" and self.jwt_secret_key.startswith("dev-only"):
            raise ValueError("JWT_SECRET_KEY must be set outside development")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def minio_health_url(self) -> str:
        scheme = "https" if self.minio_secure else "http"
        return f"{scheme}://{self.minio_endpoint}/minio/health/live"


@lru_cache
def get_settings() -> Settings:
    return Settings()
