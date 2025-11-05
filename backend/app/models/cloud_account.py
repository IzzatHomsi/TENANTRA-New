from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.db.base_class import Base


class CloudAccount(Base):
    """Represents a cloud connector configured for a tenant."""

    __tablename__ = "cloud_accounts"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    provider = Column(String(32), nullable=False)
    account_identifier = Column(String(255), nullable=False)
    status = Column(String(32), nullable=False, default="pending")
    last_synced_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    credential_reference = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="cloud_accounts")
    assets = relationship("CloudAsset", back_populates="account", cascade="all, delete-orphan")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "tenant_id": self.tenant_id,
            "provider": self.provider,
            "account_identifier": self.account_identifier,
            "status": self.status,
            "last_synced_at": self.last_synced_at.isoformat() if self.last_synced_at else None,
            "credential_reference": self.credential_reference,
            "notes": self.notes,
        }


class CloudAsset(Base):
    """Discovered asset belonging to a cloud account."""

    __tablename__ = "cloud_assets"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("cloud_accounts.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)
    asset_type = Column(String(128), nullable=False)
    region = Column(String(64), nullable=True)
    status = Column(String(32), nullable=True)
    metadata_json = Column("metadata", Text, nullable=True)
    discovered_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    account = relationship("CloudAccount", back_populates="assets")

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "account_id": self.account_id,
            "name": self.name,
            "asset_type": self.asset_type,
            "region": self.region,
            "status": self.status,
            "metadata": self.metadata_json,
            "discovered_at": self.discovered_at.isoformat() if self.discovered_at else None,
        }

