"""Settings behaviour tests."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_postgres_url_is_normalised_to_asyncpg() -> None:
    settings = Settings(
        database_url="postgres://user:pass@host:5432/db",
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_plain_postgresql_url_is_normalised() -> None:
    settings = Settings(
        database_url="postgresql://user:pass@host:5432/db",
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.database_url == "postgresql+asyncpg://user:pass@host:5432/db"


def test_production_rejects_weak_secret() -> None:
    with pytest.raises(ValidationError):
        Settings(
            environment="production",
            secret_key="change-me",
            _env_file=None,  # type: ignore[call-arg]
        )


def test_production_accepts_strong_secret() -> None:
    settings = Settings(
        environment="production",
        secret_key="a" * 40,
        _env_file=None,  # type: ignore[call-arg]
    )
    assert settings.is_production
