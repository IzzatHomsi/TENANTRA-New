from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, Index
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ProcessSnapshot(Base, TimestampMixin, ModelMixin):
    """Point-in-time inventory of processes reported by an agent."""

    __tablename__ = "process_snapshots"
    __table_args__ = (
        Index("ix_process_snapshot_agent_time", "tenant_id", "agent_id", "collected_at"),
        Index("ix_process_snapshot_report", "report_id"),
    )

    id: int = Column(Integer, primary_key=True, index=True)
    tenant_id: int = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    agent_id: int = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    report_id: str = Column(String(64), nullable=False)
    process_name: str = Column(String(255), nullable=False)
    pid: int = Column(Integer, nullable=False)
    executable_path: Optional[str] = Column(Text, nullable=True)
    username: Optional[str] = Column(String(255), nullable=True)
    hash: Optional[str] = Column(String(128), nullable=True)
    command_line: Optional[str] = Column(Text, nullable=True)
    collected_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant", back_populates="process_snapshots")
    agent = relationship("Agent", back_populates="process_snapshots")
