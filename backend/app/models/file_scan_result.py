from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from app.db.base_class import Base
from datetime import datetime  # ✅ FIXED

class FileScanResult(Base):
    __tablename__ = "file_scan_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, nullable=False)
    path = Column(String, nullable=False)
    status = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
