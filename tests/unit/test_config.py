"""Unit tests for configuration and database URL normalization."""

import pytest
from agent72.core.config import Settings


def test_default_settings():
    settings = Settings(_env_file=None)
    assert settings.PROJECT_NAME == "Agent 72: Strategic Planning Agent"
    assert settings.is_sqlite is True
    assert settings.is_postgres is False
    assert settings.AI_PROVIDER_TYPE == "mock"


def test_neon_postgresql_url_normalization():
    # Test standard postgresql url normalization
    neon_url = "postgresql://user:secret@ep-cool-sample.us-east-2.aws.neon.tech/neondb?sslmode=require"
    s = Settings(DATABASE_URL=neon_url)
    assert s.DATABASE_URL.startswith("postgresql+psycopg://")
    assert s.is_postgres is True
    assert s.is_sqlite is False

    # Test postgres:// shorthand normalization
    postgres_shorthand = "postgres://user:secret@ep-cool-sample.us-east-2.aws.neon.tech/neondb?sslmode=require"
    s2 = Settings(DATABASE_URL=postgres_shorthand)
    assert s2.DATABASE_URL.startswith("postgresql+psycopg://")
    assert s2.is_postgres is True


def test_sqlite_url_normalization():
    sqlite_url = "sqlite:///./agent72.db"
    s = Settings(DATABASE_URL=sqlite_url)
    assert s.DATABASE_URL == "sqlite:///./agent72.db"
    assert s.is_sqlite is True
    assert s.is_postgres is False
