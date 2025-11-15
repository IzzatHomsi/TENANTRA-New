from datetime import datetime
import json

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base
from app.models.base import TimestampMixin, ModelMixin


class ScanModuleResult(Base, TimestampMixin, ModelMixin):
    __tablename__ = "scan_module_results"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=True, index=True)
    module_id = Column(Integer, ForeignKey("modules.id", ondelete="CASCADE"), nullable=False, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="SET NULL"), nullable=True, index=True)
    status = Column(String(50), nullable=False)
    details = Column(Text, nullable=True)
    recorded_at = Column(DateTime, nullable=False)

    module = relationship("Module", back_populates="scan_results")

    def details_as_dict(self) -> dict:
        if not self.details:
            return {}
        try:
            return json.loads(self.details)
        except ValueError:
            return {"raw": self.details}