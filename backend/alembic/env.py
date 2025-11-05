# backend/alembic/env.py
"""
Alembic environment: robust DATABASE_URL resolution.

Resolution order:
  1) DATABASE_URL (env)
  2) POSTGRES_* envs -> build DSN (postgresql://user:pass@host:port/db)
  3) alembic.ini sqlalchemy.url (read RAW to avoid ConfigParser interpolation)

This avoids ConfigParser interpolation errors when sqlalchemy.url contains
'%(...)s' placeholders (e.g., %(DATABASE_URL)s) and supports 12‑factor style envs.
"""

import os
import sys
from logging.config import fileConfig
from alembic import context
from sqlalchemy import create_engine, pool

# Ensure backend root on sys.path so "app" package is importable
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.append(BACKEND_ROOT)

# Interpret the config file for Python logging.
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import models' MetaData for 'autogenerate' support
target_metadata = None
try:
    from app.db.base_class import Base as _Base  # type: ignore
    target_metadata = _Base.metadata
except Exception:
    target_metadata = None


def _build_from_postgres_env() -> str | None:
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB") or os.getenv("POSTGRES_DATABASE") or os.getenv("POSTGRES_DBNAME")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")
    if user and password and db:
        return f"postgresql://{user}:{password}@{host}:{port}/{db}"
    return None


def _get_database_url() -> str:
    # Prefer application-level resolution (respects secret files and overrides)
    try:
        from app.database import DATABASE_URL as APP_DATABASE_URL  # type: ignore
        if APP_DATABASE_URL:
            return APP_DATABASE_URL
    except Exception:
        pass
    # 1) DATABASE_URL from environment
    env_url = os.getenv("DATABASE_URL")
    if env_url:
        return env_url

    # 2) Construct from POSTGRES_* envs commonly present in docker-compose
    built = _build_from_postgres_env()
    if built:
        return built

    # 3) Fallback to alembic.ini sqlalchemy.url read RAW (no interpolation)
    try:
        ini_raw = config.file_config.get(config.config_ini_section, "sqlalchemy.url", raw=True)  # type: ignore[attr-defined]
    except Exception:
        ini_raw = ""

    if ini_raw:
        # If the raw value contains interpolation markers like %(DATABASE_URL)s and we still
        # don't have the env var, this will be unusable at runtime. Surface a clear error.
        if "%(" in ini_raw and ")s" in ini_raw and not os.getenv("DATABASE_URL"):
            raise RuntimeError(
                "DATABASE_URL is not set and alembic.ini sqlalchemy.url contains placeholders. "
                "Provide DATABASE_URL or POSTGRES_* envs."
            )
        return ini_raw

    raise RuntimeError(
        "DATABASE_URL is not set; POSTGRES_* envs missing; and alembic.ini has no usable sqlalchemy.url"
    )


def run_migrations_online() -> None:
    connectable = create_engine(_get_database_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    raise RuntimeError("Offline migrations are disabled; run with a live DB.")
else:
    run_migrations_online()
