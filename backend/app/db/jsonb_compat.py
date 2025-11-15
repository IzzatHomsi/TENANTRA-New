"""Compatibility helpers for PostgreSQL-only column types.

SQLite is used for local + CI tests, but several models rely on JSONB.
Register a fallback compiler so CREATE TABLE succeeds under SQLite.
"""

from sqlalchemy.dialects.postgresql import JSONB as PG_JSONB
from sqlalchemy.ext.compiler import compiles


@compiles(PG_JSONB, "sqlite")  # pragma: no cover - compile hook
def _render_sqlite_jsonb(_type, compiler, **kw):
    # SQLite supports a native JSON data type (alias of TEXT); use it so DDL succeeds.
    return "JSON"
