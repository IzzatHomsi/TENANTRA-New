from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin

class FileVisibilityResult(Base, TimestampMixin, ModelMixin):
    __tablename__ = "file_visibility_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    file_path = Column(String, nullable=False)
    share_name = Column(String, nullable=True)
    recorded_at = Column(DateTime, nullable=False)
