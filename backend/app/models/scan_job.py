from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin
from sqlalchemy.dialects.postgresql import JSONB


class ScanJob(Base, TimestampMixin, ModelMixin):
    """Represents a scheduled or on-demand scan orchestration job."""

    __tablename__ = "scan_jobs"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    scan_type = Column(String(64), nullable=False)
    priority = Column(String(32), nullable=False, default="normal")
    schedule = Column(String(128), nullable=True)
    status = Column(String(32), nullable=False, default="pending")
    created_by = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True, index=True)
    parameters = Column(JSONB, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True, server_default=expression.true())
    next_run_at = Column(DateTime, nullable=True)
    last_run_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="scan_jobs")
    creator = relationship("User", backref="scan_jobs")
    module = relationship("Module")
    agent = relationship("Agent", backref="assigned_jobs")
    results = relationship("ScanResult", back_populates="job", cascade="all, delete-orphan")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "name": self.name,
            "description": self.description,
            "scan_type": self.scan_type,
            "priority": self.priority,
            "schedule": self.schedule,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "module_id": self.module_id,
            "agent_id": self.agent_id,
            "parameters": self.parameters,
            "enabled": bool(self.enabled),
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
        }


class ScanResult(Base, TimestampMixin, ModelMixin):
    """Individual scan execution result for a specific agent or asset."""

    __tablename__ = "scan_results_v2"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("scan_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(32), nullable=False, default="queued")
    details = Column(Text, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    job = relationship("ScanJob", back_populates="results")
    agent = relationship("Agent", back_populates="scan_results")
    asset = relationship("Asset", back_populates="scan_results")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "job_id": self.job_id,
            "agent_id": self.agent_id,
            "asset_id": self.asset_id,
            "status": self.status,
            "details": self.details,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
