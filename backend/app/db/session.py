# backend/app/db/session.py
# Engine + Session factory + helpers, with no model imports.

import os
from contextlib import contextmanager
from urllib.parse import urlparse, urlunparse, quote
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def _build_database_url() -> str:
    """
    Construct a SQLAlchemy-compatible database URL from environment
    variables.  This helper supports both a file-based password (via
    ``POSTGRES_PASSWORD_FILE``) and direct password injection (via
    ``POSTGRES_PASSWORD``).  If a complete ``DATABASE_URL`` or ``DB_URL``
    environment variable is provided, it will take precedence.

    The fallback connection string uses sane defaults for the Tenantra
    development environment (user/db ``tenantra`` on host ``db`` at
    port 5432).  See the `docker-compose.yml` for corresponding
    environment variables.

    :return: A database URL suitable for SQLAlchemy's create_engine.
    """
    # First honor explicit overrides
    explicit = os.getenv("DATABASE_URL") or os.getenv("DB_URL")
    if explicit:
        parsed = urlparse(explicit)
        scheme = parsed.scheme
        if scheme.startswith("postgresql") and "+" not in scheme:
            scheme = "postgresql+psycopg"
            explicit = urlunparse(
                (scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment)
            )
        return explicit

    # Read core connection parameters from environment, falling back
    # to Tenantra's defaults.  These names mirror the variables used
    # in the Docker Compose configuration.  DO NOT hardcode secrets here.
    user = os.getenv("POSTGRES_USER", "tenantra")
    database = os.getenv("POSTGRES_DB", "tenantra")
    host = os.getenv("POSTGRES_HOST", "db")
    port = os.getenv("POSTGRES_PORT", "5432")

    # Determine the password: prefer reading from a file for security.
    password: str = ""
    pwd_file = os.getenv("POSTGRES_PASSWORD_FILE")
    if pwd_file:
        try:
            with open(pwd_file, "r", encoding="utf-8") as fh:
                password = fh.read().strip()
        except FileNotFoundError:
            password = os.getenv("POSTGRES_PASSWORD", "")
    else:
        # Also consider Docker secrets default path
        if os.path.isfile("/run/secrets/db_password"):
            try:
                with open("/run/secrets/db_password", "r", encoding="utf-8") as fh:
                    password = fh.read().strip()
            except Exception:
                password = os.getenv("POSTGRES_PASSWORD", "")
        else:
            password = os.getenv("POSTGRES_PASSWORD", "")

    # If an explicit URL was provided, enforce our resolved password into it (if any)
    if explicit:
        try:
            parts = urlparse(explicit)
            netloc = parts.netloc
            if password and "@" in netloc:
                creds, hostport = netloc.split("@", 1)
                if ":" in creds:
                    user, _ = creds.split(":", 1)
                else:
                    user = creds
                netloc = f"{user}:{quote(password, safe='')}@{hostport}"
                return urlunparse((parts.scheme, netloc, parts.path, parts.params, parts.query, parts.fragment))
        except Exception:
            # Fall back to constructing from parts when parsing fails
            pass
        # No password to enforce or parse failed; return explicit as-is
    # Build the DSN.  Use psycopg (psycopg3) driver by default.
    if password:
        return f"postgresql+psycopg://{user}:{quote(password, safe='')}@{host}:{port}/{database}"
    else:
        return f"postgresql+psycopg://{user}@{host}:{port}/{database}"


# Construct the database URL using the helper above.  SQLAlchemy will
# internally escape special characters in the password as needed.
DATABASE_URL = _build_database_url()
# Emit a short masked DSN debug for diagnostics
try:
    parts = urlparse(DATABASE_URL)
    netloc = parts.netloc
    if "@" in netloc:
        creds, hostport = netloc.split("@", 1)
        if ":" in creds:
            u, _ = creds.split(":", 1)
            netloc = f"{u}:***@{hostport}"
        else:
            netloc = f"{creds}@{hostport}"
    masked = urlunparse((parts.scheme, netloc, parts.path, parts.params, parts.query, parts.fragment))
    print(f"[db.session] url={masked}")
except Exception:
    pass

# Create the SQLAlchemy engine and session factory.  Enable
# ``pool_pre_ping`` so that connections are automatically refreshed if
# the underlying TCP connection drops (e.g. after network hiccups).
engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_db():
    """FastAPI dependency: yields a session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def get_db_session():
    """Script/worker helper: with get_db_session() as db: ..."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
