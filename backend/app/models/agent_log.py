from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    severity = Column(String, default="info")  # info, warning, error
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    agent = relationship("Agent", back_populates="logs")
