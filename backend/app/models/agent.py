from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import secrets
from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class Agent(Base, TimestampMixin, ModelMixin):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    def _generate_token() -> str:
        return secrets.token_hex(16)

    token = Column(String(128), nullable=False, unique=True, default=_generate_token)
    ip_address = Column(String, nullable=True)
    os = Column(String, nullable=True)
    version = Column(String, nullable=True)
    status = Column(String, default="active")
    last_seen_at = Column(DateTime, nullable=True)

    logs = relationship("AgentLog", back_populates="agent")
    registry_snapshots = relationship("RegistrySnapshot", back_populates="agent", cascade="all, delete-orphan")
    boot_configs = relationship("BootConfig", back_populates="agent", cascade="all, delete-orphan")
    integrity_events = relationship("IntegrityEvent", back_populates="agent", cascade="all, delete-orphan")
    service_snapshots = relationship("ServiceSnapshot", back_populates="agent", cascade="all, delete-orphan")
    task_snapshots = relationship("TaskSnapshot", back_populates="agent", cascade="all, delete-orphan")
    process_snapshots = relationship("ProcessSnapshot", back_populates="agent", cascade="all, delete-orphan")
    process_baselines = relationship("ProcessBaseline", back_populates="agent", cascade="all, delete-orphan")
    process_drift_events = relationship("ProcessDriftEvent", back_populates="agent", cascade="all, delete-orphan")
    scan_results = relationship("ScanResult", back_populates="agent", cascade="all, delete-orphan")

    tenant = relationship("Tenant", back_populates="agents")
