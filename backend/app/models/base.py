"""Shared SQLAlchemy mixins."""

from __future__ import annotations

import os
from datetime import datetime
from functools import lru_cache
from typing import Any

from sqlalchemy import Column, DateTime, text
from sqlalchemy.orm import declared_attr

from app.db.base_class import Base  # re-export for legacy imports

def _resolve_timestamp_default() -> str:
    """Choose a SQL clause that works for the active database backend."""

    # Respect explicit test/database overrides first so sqlite-based tests can
    # create tables without failing on PostgreSQL-only functions.
    for key in ("TENANTRA_TEST_DB_URL", "DB_URL", "DATABASE_URL", "SQLALCHEMY_DATABASE_URI"):
        url = os.getenv(key)
        if url:
            return url.lower()
    return ""


@lru_cache(maxsize=2)
def _timestamp_server_default():
    url = _resolve_timestamp_default()
    if url.startswith("sqlite"):
        # SQLite lacks timezone() helper; CURRENT_TIMESTAMP keeps compatibility.
        return text("CURRENT_TIMESTAMP")
    return text("timezone('utc', now())")


_UTC_NOW = _timestamp_server_default()


class TimestampMixin:
    """Adds created_at/updated_at columns unless a model opts out."""

    @staticmethod
    def _timestamps_enabled(cls: type[Any]) -> bool:
        return getattr(cls, "__timestamped__", True)

    @declared_attr.directive
    def created_at(cls):
        if not TimestampMixin._timestamps_enabled(cls):
            return cls.__dict__.get("created_at")
        existing = cls.__dict__.get("created_at")
        if isinstance(existing, Column):
            return existing
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
            server_default=_UTC_NOW,
        )

    @declared_attr.directive
    def updated_at(cls):
        if not TimestampMixin._timestamps_enabled(cls):
            return cls.__dict__.get("updated_at")
        existing = cls.__dict__.get("updated_at")
        if isinstance(existing, Column):
            return existing
        return Column(
            DateTime(timezone=True),
            nullable=False,
            default=datetime.utcnow,
            onupdate=datetime.utcnow,
            server_default=_UTC_NOW,
        )


class ModelMixin:
    """Convenience helpers for repr/dict conversions."""

    def __repr__(self) -> str:
        values = []
        for column in self.__table__.columns:
            values.append(f"{column.name}={getattr(self, column.name)!r}")
        return f"<{self.__class__.__name__}({', '.join(values)})>"

    def as_dict(self) -> dict[str, Any]:
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
