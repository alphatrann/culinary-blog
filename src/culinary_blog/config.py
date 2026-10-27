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
    # Pre-ping costs 3 extra round trips (BEGIN; ; ROLLBACK) on every pool checkout - most of a read request's DB
    # spans in the M6a traces. Off by default; `pool_recycle` bounds connection age instead. Turn on if the DB is
    # restarted often (a stale connection then fails the first request that draws it).
    db_pool_pre_ping: bool = False
    db_pool_recycle_seconds: int = 1800

    cache_redis_url: str = "redis://localhost:6380/0"
    # A dead Cache Redis must cost milliseconds, not a hang on the OS connect timeout (NFR-REL-002).
    cache_socket_timeout_seconds: float = 0.25
    # ADR-0003 TTL tiers. Overridable only so load tests can force expiry churn; keep the defaults in production.
    cache_ttl_categories_seconds: int = 3600
    cache_ttl_recipes_seconds: int = 1800
    cache_ttl_search_seconds: int = 300
    queue_redis_url: str = "redis://localhost:6381/0"
    ratelimit_redis_url: str = "redis://localhost:6382/0"
    # Fail-open (SRS 3.x): a dead Rate Limit Redis must cost milliseconds, then let the request through.
    # HMAC key that pseudonymises client IPs in rate-limit keys. Separate from the JWT secret so rotating one doesn't
    # affect the other. Generate with `openssl rand -hex 32`.
    ratelimit_hash_key: str = "dev-only-insecure-ratelimit-key"
    ratelimit_socket_timeout_seconds: float = 0.25
    # NFR-SEC-003 / ADR-0006. Window is 60s everywhere; counter keys live 90s so the previous window stays readable.
    auth_rate_limit_per_minute: int = 10
    api_rate_limit_per_minute: int = 100
    upload_rate_limit_per_minute: int = 5
    rate_limit_window_seconds: int = 60
    rate_limit_key_ttl_seconds: int = 90
    # Peers whose X-Forwarded-For we believe (IPs/CIDRs, comma separated): loopback + private ranges, i.e. nginx.
    trusted_proxies: str = "127.0.0.0/8,::1/128,10.0.0.0/8,172.16.0.0/12,192.168.0.0/16,fc00::/7"

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
    # FR-AUTH-003. Empty disables Google sign-in (the endpoint answers 503); the audience check needs this value.
    google_client_id: str = ""

    @model_validator(mode="after")
    def _require_real_secret_outside_development(self) -> "Settings":
        if self.environment != "development" and self.jwt_secret_key.startswith("dev-only"):
            raise ValueError("JWT_SECRET_KEY must be set outside development")
        if self.environment != "development" and self.ratelimit_hash_key.startswith("dev-only"):
            raise ValueError("RATELIMIT_HASH_KEY must be set outside development")
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def trusted_proxy_list(self) -> list[str]:
        return [item.strip() for item in self.trusted_proxies.split(",") if item.strip()]

    @property
    def minio_health_url(self) -> str:
        scheme = "https" if self.minio_secure else "http"
        return f"{scheme}://{self.minio_endpoint}/minio/health/live"


@lru_cache
def get_settings() -> Settings:
    return Settings()
