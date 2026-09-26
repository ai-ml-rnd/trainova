"""Application configuration."""

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_name: str = "Forge API"
    app_version: str = "0.1.0"
    debug: bool = Field(default=False)
    environment: str = Field(default="development")

    # Server
    host: str = Field(default="0.0.0.0")
    port: int = Field(default=8000)
    workers: int = Field(default=1)

    # Database
    database_url: PostgresDsn = Field(
        default="postgresql://forge:forge@localhost:5432/forge"
    )
    database_pool_size: int = Field(default=10)
    database_max_overflow: int = Field(default=20)

    # Redis/Valkey
    redis_url: str = Field(default="redis://localhost:6379/0")

    # LiteLLM
    litellm_url: str = Field(default="http://localhost:4000")
    litellm_timeout: int = Field(default=60)

    # Object storage
    s3_endpoint: str = Field(default="http://localhost:8333")
    s3_access_key: str = Field(default="minioadmin")
    s3_secret_key: str = Field(default="minio-password")
    s3_bucket: str = Field(default="forge-dev")

    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production")
    jwt_algorithm: str = Field(default="HS256")
    jwt_expiration: int = Field(default=3600)  # 1 hour

    # Tenant
    default_tenant_id: str = Field(default="00000000-0000-0000-0000-000000000000")

    # Observability
    otel_endpoint: str = Field(default="http://localhost:4317")
    otel_enabled: bool = Field(default=True)
    langfuse_host: str = Field(default="http://localhost:3000")

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_debug(self) -> bool:
        return self.debug or not self.is_production


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
