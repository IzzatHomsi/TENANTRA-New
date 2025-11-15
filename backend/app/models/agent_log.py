from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin

class AgentLog(Base, TimestampMixin, ModelMixin):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    severity = Column(String, default="info")  # info, warning, error
    message = Column(Text, nullable=False)

    agent = relationship("Agent", back_populates="logs")
