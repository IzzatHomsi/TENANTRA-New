# backend/app/db/__init__.py
# Re-export Base eagerly; other DB primitives are loaded lazily
# so modules like alembic/env.py can import Base without triggering session imports.

from .base_class import Base  # safe: no models imported here

__all__ = ["Base", "engine", "SessionLocal", "get_db", "get_db_session"]

def __getattr__(name: str):
    if name in {"engine", "SessionLocal", "get_db", "get_db_session"}:
        # Import on first access to avoid circular import during package init
        from .session import engine, SessionLocal, get_db, get_db_session
        mapping = {
            "engine": engine,
            "SessionLocal": SessionLocal,
            "get_db": get_db,
            "get_db_session": get_db_session,
        }
        return mapping[name]
    raise AttributeError(name)
