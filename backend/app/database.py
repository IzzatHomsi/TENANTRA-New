"""
Database configuration for the Tenantra backend.

This module is responsible for constructing a SQLAlchemy engine and session
factory using connection details sourced from environment variables.  The
previous implementation hard‑coded the database connection string, which
made it difficult to override in different environments.  As part of the
Batch 5.5.6 improvements we now assemble the connection string from
environment variables with sensible defaults.  If a full DB_URL is
provided it will be honoured, otherwise the individual pieces
(POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, DB_HOST, DB_PORT) are
combined to form a PostgreSQL URL.  This logic means that the same code
can be used in development, testing and production without modification.

The `get_db` generator yields a database session and ensures it is
cleanly closed after use.
"""

import os
import sys
from pathlib import Path
from urllib.parse import urlparse, urlunparse, quote
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# Retrieve individual connection details or a complete URL from the
# environment.  `DB_URL` takes precedence when defined.
POSTGRES_USER = os.getenv("POSTGRES_USER", "tenantra")
# Resolve password from secret file first (if present), then env, then fallback
_pw_file = os.getenv("POSTGRES_PASSWORD_FILE")
_pw = None
_pw_src = None
try:
    if _pw_file and Path(_pw_file).is_file():
        _pw = Path(_pw_file).read_text(encoding="utf-8").strip()
        _pw_src = f"file:{_pw_file}"
    elif Path("/run/secrets/db_password").is_file():
        _pw = Path("/run/secrets/db_password").read_text(encoding="utf-8").strip()
        _pw_src = "/run/secrets/db_password"
except Exception:
    _pw = None
if not _pw:
    _pw = os.getenv("POSTGRES_PASSWORD")
    if _pw:
        _pw_src = "env:POSTGRES_PASSWORD"
POSTGRES_PASSWORD = _pw or os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tenantra")
# Prefer DB_HOST if provided, fall back to POSTGRES_HOST for
# backwards-compatibility, then to the Docker service name ``db``.
POSTGRES_HOST = os.getenv("DB_HOST", os.getenv("POSTGRES_HOST", "db"))
POSTGRES_PORT = os.getenv("DB_PORT", "5432")

# Read explicit URLs first if provided
DATABASE_URL = os.getenv("DB_URL") or os.getenv("DATABASE_URL")


def _ensure_psycopg_scheme(url: str) -> str:
    if not url:
        return url
    parsed = urlparse(url)
    scheme = parsed.scheme
    if scheme.startswith("postgresql") and "+" not in scheme:
        scheme = "postgresql+psycopg"
        url = urlunparse((scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
    return url

# Prefer an in-process SQLite DB for unit tests unless explicitly overridden
if (os.getenv("PYTEST_CURRENT_TEST") or os.getenv("TENANTRA_TEST_BOOTSTRAP")) and not DATABASE_URL:
    DATABASE_URL = "sqlite:///./test_api.db"

# Assemble the database URL.  Users may specify a full ``DB_URL`` (e.g.
# ``postgresql://user:pass@host:port/db``) or rely on the individual
# variables above.  If ``DB_URL`` exists it overrides the others.
# If still not set, assemble from parts
if not DATABASE_URL:
    # Assemble a safe default using resolved password
    if POSTGRES_PASSWORD:
        safe_password = quote(POSTGRES_PASSWORD, safe="")
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{safe_password}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        # omit password section if not provided
        DATABASE_URL = f"postgresql://{POSTGRES_USER}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
else:
    # If we have a secret-derived password, enforce it into the URL to prevent mismatches
    if POSTGRES_PASSWORD:
        try:
            parsed = urlparse(DATABASE_URL)
            # preserve driver prefix if present (e.g., postgresql+psycopg2)
            scheme = parsed.scheme
            netloc = parsed.netloc
            if "@" in netloc:
                creds, hostport = netloc.split("@", 1)
                if ":" in creds:
                    user, _oldpw = creds.split(":", 1)
                else:
                    user = creds
                netloc = f"{user}:{quote(POSTGRES_PASSWORD, safe='')}@{hostport}"
                DATABASE_URL = urlunparse((scheme, netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        except Exception:
            # fall back to assembling from parts
            DATABASE_URL = f"postgresql://{POSTGRES_USER}:{quote(POSTGRES_PASSWORD, safe='')}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

DATABASE_URL = _ensure_psycopg_scheme(DATABASE_URL)

# Emit a one-line debug to stdout about how DB connection was constructed (redacted)
try:
    _host = POSTGRES_HOST
    _user = POSTGRES_USER
    _has_pw = bool(POSTGRES_PASSWORD)
    _masked = DATABASE_URL
    try:
        parts = urlparse(DATABASE_URL)
        netloc = parts.netloc
        if "@" in netloc:
            creds, hostport = netloc.split("@", 1)
            if ":" in creds:
                u, _p = creds.split(":", 1)
                netloc = f"{u}:***@{hostport}"
            else:
                netloc = f"{creds}@{hostport}"
        _masked = urlunparse((parts.scheme, netloc, parts.path, parts.params, parts.query, parts.fragment))
    except Exception:
        pass
    sys.stdout.write(f"[database] DSN host={_host} user={_user} pw={'yes' if _has_pw else 'no'} src={_pw_src or 'n/a'} url={_masked}\n")
    sys.stdout.flush()
except Exception:
    pass

# Create the SQLAlchemy engine and session factory.  The ``autocommit`` and
# ``autoflush`` flags are kept consistent with the original code.
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False, "timeout": 30}
    # Use StaticPool for both file and in-memory SQLite during tests to avoid locking
    engine: Engine = create_engine(
        DATABASE_URL,
        connect_args=connect_args,
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Register PostgreSQL type fallbacks (e.g., JSONB -> JSON under SQLite)
import app.db.jsonb_compat  # noqa: F401

# Base class for declarative models.  Importing from
# ``app.models.base`` ensures that all models share the same
# ``Base`` instance, avoiding multiple metadata collections and
# migration discrepancies.  Do not call ``declarative_base`` here.
from app.db.base_class import Base

def get_db():
    """Yield a SQLAlchemy session scoped to the current request or task.

    Using a generator allows FastAPI dependencies to control the lifetime
    of the session; the session is created when this function is entered
    and always closed when the caller exits the context.  Failure to
    close sessions can lead to connection leaks under high concurrency.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
