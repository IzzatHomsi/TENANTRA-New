# backend/app/db/base_class.py
# Single declarative Base for all ORM models.
# Do NOT import any models here to avoid circular imports.

from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    # Acts as the global registry for all mapped classes.
    pass
