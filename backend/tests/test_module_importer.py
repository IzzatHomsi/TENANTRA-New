"""Tests for the CSV module importer and metadata population."""

from __future__ import annotations

import uuid

from app.database import SessionLocal
from app.models.module import Module
from app.models.tenant_module import TenantModule
from scripts.import_modules_from_csv import import_modules


def test_import_modules_populates_extended_metadata(tmp_path):
    module_name = f"test_net_module_{uuid.uuid4().hex[:8]}"
    csv_path = tmp_path / "modules.csv"
    csv_path.write_text(
        "Category,Module Name,Purpose / Output Goal,Dependencies & Notes,Pre Config,Expertise Level,Team,OS,Application,Compliance Mapping,Status\n"
        f"Networking Devices,{module_name},Ensure network posture,Requires SNMP community,Configure SNMP read-only,Level 2,Networking Team,IOS,Agent (Tenantra),PCI DSS,Active\n",
        encoding="utf-8",
    )

    stats = import_modules(csv_path, dry_run=False)
    assert stats["rows"] == 1
    assert stats["created"] == 1

    session = SessionLocal()
    try:
        module = session.query(Module).filter(Module.name == module_name).one()
        assert module.purpose == "Ensure network posture"
        assert module.dependencies == "Requires SNMP community"
        assert module.preconditions == "Configure SNMP read-only"
        assert module.team == "Networking Team"
        assert module.parameter_schema is not None
        assert "targets" in module.parameter_schema.get("properties", {})
        module_id = module.id
        session.query(TenantModule).filter(TenantModule.module_id == module_id).delete(synchronize_session=False)
        session.delete(module)
        session.commit()
    finally:
        session.close()

    # Ensure removal cascaded and importer can be re-run without duplicate conflicts
    stats = import_modules(csv_path, dry_run=False)
    assert stats["created"] == 1

    session = SessionLocal()
    try:
        module = session.query(Module).filter(Module.name == module_name).one()
        module_id = module.id
        session.query(TenantModule).filter(TenantModule.module_id == module_id).delete(synchronize_session=False)
        session.delete(module)
        session.commit()
    finally:
        session.close()


def test_import_modules_handles_network_perimeter_category(tmp_path):
    module_name = "net_perimeter_demo"
    csv_path = tmp_path / "modules_network.csv"
    csv_path.write_text(
        "Category,Module Name,Purpose / Output Goal\n"
        f"Network & Perimeter Security,{module_name},Inspect edge firewall posture\n",
        encoding="utf-8",
    )

    stats = import_modules(csv_path, dry_run=False)
    assert stats["rows"] == 1

    session = SessionLocal()
    try:
        module = session.query(Module).filter(Module.name == module_name).one()
        assert module.parameter_schema is not None
        assert "targets" in module.parameter_schema.get("properties", {})
        module_id = module.id
        session.query(TenantModule).filter(TenantModule.module_id == module_id).delete(synchronize_session=False)
        session.delete(module)
        session.commit()
    finally:
        session.close()
