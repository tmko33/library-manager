"""Application configuration loaded from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings, read from the environment or a ``.env`` file."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Library Manager API"
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"
    cors_origins: list[str] = ["*"]

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/library"
    test_database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/library_test"

    # Security
    secret_key: str = "insecure-development-secret-change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Business rules
    loan_period_days: int = 14
    max_active_loans: int = 5
    fine_per_day: float = 0.50
    reservation_hold_days: int = 3

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_testing(self) -> bool:
        return self.environment == "test"

    @field_validator("database_url", "test_database_url")
    @classmethod
    def _normalise_database_url(cls, value: str) -> str:
        """Accept the URLs handed out by hosted providers (Render, Heroku)."""
        if value.startswith("postgres://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgres://")
        if value.startswith("postgresql://"):
            return "postgresql+asyncpg://" + value.removeprefix("postgresql://")
        return value

    @model_validator(mode="after")
    def _validate_production_secrets(self) -> "Settings":
        if self.environment != "production":
            return self

        insecure_markers = ("change-me", "insecure-development")
        if len(self.secret_key) < 32 or any(
            marker in self.secret_key for marker in insecure_markers
        ):
            raise ValueError("SECRET_KEY must be a strong, unique value in production.")
        return self


@lru_cache
def get_settings() -> Settings:
    """Return a cached ``Settings`` instance."""
    return Settings()


settings = get_settings()
