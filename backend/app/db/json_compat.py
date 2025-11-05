"""
Dialect-compatible JSON column type.

Provides a SQLAlchemy TypeDecorator that uses PostgreSQL JSONB when available
and falls back to generic JSON for other dialects (e.g., SQLite) used in tests.
"""
from __future__ import annotations

from sqlalchemy.types import TypeDecorator, JSON as SAJSON

try:
    from sqlalchemy.dialects.postgresql import JSONB as PGJSONB  # type: ignore
except Exception:  # pragma: no cover
    PGJSONB = None  # type: ignore


class JSONCompatible(TypeDecorator):
    impl = SAJSON
    cache_ok = True

    def load_dialect_impl(self, dialect):  # noqa: D401
        # Use JSONB on Postgres, plain JSON otherwise
        if getattr(dialect, "name", "") == "postgresql" and PGJSONB is not None:
            try:
                return dialect.type_descriptor(PGJSONB())
            except Exception:
                return dialect.type_descriptor(SAJSON())
        return dialect.type_descriptor(SAJSON())

