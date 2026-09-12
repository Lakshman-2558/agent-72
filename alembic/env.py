"""Alembic environment configuration for database migrations."""

import sys
from logging.config import fileConfig
from pathlib import Path
from alembic import context
from sqlalchemy import pool

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agent72.core.config import settings
from agent72.infrastructure.database.base import Base
# Import models to register them with Base.metadata
import agent72.infrastructure.database.models  # noqa: F401
from agent72.infrastructure.database.session import create_db_engine

# this is the Alembic Config object
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=settings.is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = create_db_engine(settings.DATABASE_URL)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=settings.is_sqlite,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
