from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base              # ✅ CHANGED: unified Base

class Asset(Base):
    __tablename__ = "assets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    ip_address = Column(String(45), nullable=True)
    os = Column(String(100), nullable=True)
    hostname = Column(String(255), nullable=True)
    last_seen = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="assets")
    scan_results = relationship("ScanResult", back_populates="asset", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Asset(id={self.id}, name={self.name}, tenant_id={self.tenant_id})>"
