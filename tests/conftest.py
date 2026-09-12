"""Pytest fixtures and configuration for Agent 72 test suite."""

from typing import Generator
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool, event
from sqlalchemy.orm import sessionmaker, Session

from agent72.infrastructure.database.base import Base
from agent72.infrastructure.database.session import get_db
from agent72.api.dependencies import get_ai
from agent72.infrastructure.ai.mock_provider import MockAIProvider
from agent72.main import app

# Create in-memory SQLite engine with StaticPool for fast, isolated tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


@event.listens_for(test_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.close()


TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Provides a fresh, isolated database session per test function."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def mock_ai():
    """Provides a deterministic mock AI provider."""
    return MockAIProvider(model_name="mock-test-v1")


@pytest.fixture(scope="function")
def client(db_session: Session, mock_ai: MockAIProvider) -> Generator[TestClient, None, None]:
    """Provides a TestClient with dependency overrides for database and AI provider."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_ai():
        return mock_ai

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_ai] = override_get_ai

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
