# backend/app/models/base.py
# Single source of truth for ORM mixins. Imports the canonical Base from app.db.base_class.

from datetime import datetime                  # Used for UTC timestamp defaults
from sqlalchemy import Column, DateTime        # SQLAlchemy column types for timestamps
from app.db.base_class import Base             # ✅ THE ONLY Base used by all models

class TimestampMixin:
    """Adds created_at and updated_at UTC timestamp columns to a model."""
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)                 # set at insert
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow,                 # set at insert
                        onupdate=datetime.utcnow)                                          # auto-update on change

class ModelMixin:
    """Convenience helpers for __repr__ and dict serialisation."""
    def __repr__(self) -> str:
        # Produce a helpful debug string like: <User(id=1, username='admin', ...)>
        values = []
        for column in self.__table__.columns:
            values.append(f"{column.name}={getattr(self, column.name)!r}")
        return f"<{self.__class__.__name__}({', '.join(values)})>"

    def as_dict(self) -> dict:
        # Convert ORM instance to a simple dict of column->value pairs
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
