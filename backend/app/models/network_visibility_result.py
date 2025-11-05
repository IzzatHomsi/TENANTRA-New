from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from datetime import datetime  # ✅ FIXED

class NetworkVisibilityResult(Base):
    __tablename__ = "network_visibility_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    port = Column(Integer, nullable=False)
    service = Column(String, nullable=True)
    status = Column(String(50), nullable=True)
    recorded_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
