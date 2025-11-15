from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin

class NetworkVisibilityResult(Base, TimestampMixin, ModelMixin):
    __tablename__ = "network_visibility_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True)
    port = Column(Integer, nullable=False)
    service = Column(String, nullable=True)
    status = Column(String(50), nullable=True)
    recorded_at = Column(DateTime, nullable=False)
