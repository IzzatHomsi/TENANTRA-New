from sqlalchemy import Column, Integer, String

from app.db.base_class import Base              # ✅ CHANGED: unified Base
from app.models.base import TimestampMixin, ModelMixin

class Role(Base, TimestampMixin, ModelMixin):
    """User role within the Tenantra platform (e.g., admin, standard_user)."""

    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
