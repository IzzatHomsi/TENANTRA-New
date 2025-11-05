from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from app.db.json_compat import JSONCompatible
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ScheduledScan(Base, TimestampMixin, ModelMixin):
    __tablename__ = "scheduled_scans"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="SET NULL"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="SET NULL"), nullable=True)
    cron_expr = Column(String(128), nullable=False)
    status = Column(String(32), nullable=False, default="scheduled")
    enabled = Column(Boolean, nullable=False, default=True)
    parameters = Column(JSONCompatible(), nullable=True)
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)

    module = relationship("Module", back_populates="scheduled_scans", lazy="joined", uselist=False)
