from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from datetime import datetime  # ✅ FIXED

class NetworkScanResult(Base):
    __tablename__ = "network_scan_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False)
    port = Column(Integer, nullable=False)
    protocol = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
