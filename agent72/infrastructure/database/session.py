"""Database session and engine management supporting SQLite and Neon PostgreSQL."""

from typing import Generator
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from agent72.core.config import settings
from agent72.core.logging import get_logger

logger = get_logger(__name__)


def create_db_engine(database_url: str):
    """
    Factory creating a SQLAlchemy engine configured appropriately
    for SQLite (local development/tests) or PostgreSQL (Neon production).
    """
    if database_url.startswith("sqlite"):
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False},
            echo=settings.DB_ECHO,
        )

        # Enforce foreign key constraints in SQLite for parity with PostgreSQL
        @event.listens_for(engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON;")
            cursor.close()

        logger.info("Configured SQLite database engine with foreign key enforcement.")
        return engine

    else:
        # PostgreSQL / Neon configuration
        # pool_pre_ping=True is essential for Neon serverless postgres to prevent stale connections
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            echo=settings.DB_ECHO,
        )
        logger.info("Configured PostgreSQL / Neon database engine with connection pooling and pre-ping.")
        return engine


engine = create_db_engine(settings.DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency providing a transactional database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
