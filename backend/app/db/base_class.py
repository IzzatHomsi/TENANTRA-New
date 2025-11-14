# backend/app/db/base_class.py
# Single declarative Base for all ORM models.
# Do NOT import any models here to avoid circular imports.

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""

    __abstract__ = True
