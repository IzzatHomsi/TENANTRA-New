"""Import Tenantra modules from the master CSV."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Optional

from app.database import SessionLocal
from app.models.module import Module
from app.models.tenant import Tenant
from app.models.tenant_module import TenantModule
from app.services.module_metadata import get_parameter_schema_for_category

COLUMN_ALIASES: Dict[str, Iterable[str]] = {
    "module_id": ["module_id", "module id", "id"],
    "module_name": ["module_name", "module name", "name"],
    "category": ["category"],
    "phase": ["phase", "phase id", "phase number"],
    "impact_level": ["impact_level", "impact level", "expertise level"],
    "path": ["path", "module path"],
    "status": ["status", "state"],
    "last_update": ["last_update", "last update", "updated", "last modified"],
    "description": [
        "description",
        "Purpose / Output Goal",
        "purpose / output goal",
        "purpose",
        "summary",
    ],
    "dependencies": ["Dependencies & Notes", "dependencies", "notes"],
    "compliance_mapping": ["Compliance Mapping", "compliance mapping"],
    "preconditions": ["Pre Config", "pre-config", "pre configuration", "preconfiguration", "prerequisites", "pre req"],
    "team": ["team", "owner", "responsible team"],
    "operating_systems": ["os", "operating systems", "supported os", "platform"],
    "application_target": ["application", "component", "stack"],
}

MANDATORY_COLUMNS = {"module_name", "category"}

_DISABLED_STATUSES = {"disabled", "inactive", "retired", "deprecated"}


def _normalize(name: str) -> str:
    return name.strip().lower()


def _resolve_headers(fieldnames: Iterable[str]) -> Dict[str, str]:
    normalized = {_normalize(name): name for name in fieldnames}
    resolved: Dict[str, str] = {}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            key = _normalize(alias)
            if key in normalized:
                resolved[canonical] = normalized[key]
                break
    missing = MANDATORY_COLUMNS - set(resolved)
    if missing:
        raise ValueError(
            "CSV missing required columns: " + ", ".join(sorted(missing))
        )
    return resolved


def _parse_last_update(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    raw = value.strip()
    if not raw:
        return None
    for fmt in (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None


def _status_to_bool(status: Optional[str]) -> bool:
    status_value = (status or "").strip().lower()
    if not status_value:
        return True
    return status_value not in _DISABLED_STATUSES


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "module"


def _checksum_from_row(row: Dict[str, str]) -> str:
    hasher = hashlib.sha256()
    for key in sorted(row):
        hasher.update(key.encode("utf-8", errors="ignore"))
        hasher.update(b"=")
        hasher.update((row[key] or "").encode("utf-8", errors="ignore"))
        hasher.update(b"\0")
    return hasher.hexdigest()


def _ensure_tenant_links(db, module: Module, enabled: bool) -> None:
    tenants = db.query(Tenant).all()
    for tenant in tenants:
        link = (
            db.query(TenantModule)
            .filter(
                TenantModule.tenant_id == tenant.id,
                TenantModule.module_id == module.id,
            )
            .first()
        )
        if link:
            if link.enabled is None:
                link.enabled = enabled
            continue
        db.add(TenantModule(tenant_id=tenant.id, module_id=module.id, enabled=enabled))


def _trim(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    stripped = value.strip()
    return stripped or None


def import_modules(csv_path: Path, dry_run: bool = False) -> Dict[str, int]:
    if not csv_path.exists():
        raise FileNotFoundError(csv_path)

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise ValueError("CSV has no header row")
        resolved = _resolve_headers(reader.fieldnames)

        session = SessionLocal()
        try:
            cache_by_name = {
                (module.name or "").lower(): module
                for module in session.query(Module).all()
            }
            cache_by_external = {
                module.external_id.lower(): module
                for module in cache_by_name.values()
                if module.external_id
            }

            stats = {"created": 0, "updated": 0, "rows": 0}

            for index, row in enumerate(reader, start=1):
                stats["rows"] += 1
                name = (row.get(resolved["module_name"]) or "").strip()
                if not name:
                    raise ValueError(f"Row {index} missing module name")
                name_key = name.lower()

                external_id = None
                module_id_column = resolved.get("module_id")
                if module_id_column:
                    external_id = _trim(row.get(module_id_column))
                if not external_id:
                    external_id = f"auto-{_slugify(name)}-{index:04d}"
                external_key = external_id.lower()

                module = cache_by_external.get(external_key) or cache_by_name.get(name_key)

                created = False
                if not module:
                    module = Module(name=name, external_id=external_id)
                    session.add(module)
                    created = True
                else:
                    module.name = name
                    module.external_id = external_id

                cache_by_name[name_key] = module
                cache_by_external[external_key] = module

                module.category = _trim(row.get(resolved["category"]))

                phase_value: Optional[int] = None
                phase_column = resolved.get("phase")
                if phase_column:
                    phase_raw = _trim(row.get(phase_column))
                    if phase_raw:
                        try:
                            phase_value = int(phase_raw)
                        except ValueError:
                            phase_value = None
                module.phase = phase_value

                impact_column = resolved.get("impact_level")
                module.impact_level = _trim(row.get(impact_column)) if impact_column else None

                path_column = resolved.get("path")
                module.path = _trim(row.get(path_column)) if path_column else None

                status_column = resolved.get("status")
                status_value = _trim(row.get(status_column)) if status_column else None
                module.status = status_value or "active"
                module.enabled = _status_to_bool(status_value)

                last_update_column = resolved.get("last_update")
                module.last_update = _parse_last_update(
                    row.get(last_update_column) if last_update_column else None
                )

                description_column = resolved.get("description")
                module.purpose = _trim(row.get(description_column)) if description_column else None

                dependencies_column = resolved.get("dependencies")
                module.dependencies = _trim(row.get(dependencies_column)) if dependencies_column else None

                preconditions_column = resolved.get("preconditions")
                module.preconditions = _trim(row.get(preconditions_column)) if preconditions_column else None

                team_column = resolved.get("team")
                module.team = _trim(row.get(team_column)) if team_column else None

                os_column = resolved.get("operating_systems")
                module.operating_systems = _trim(row.get(os_column)) if os_column else None

                application_column = resolved.get("application_target")
                module.application_target = _trim(row.get(application_column)) if application_column else None

                compliance_column = resolved.get("compliance_mapping")
                module.compliance_mapping = _trim(row.get(compliance_column)) if compliance_column else None

                description_parts = []
                if module.purpose:
                    description_parts.append(module.purpose)
                if module.dependencies:
                    description_parts.append(f"Dependencies: {module.dependencies}")
                if module.preconditions:
                    description_parts.append(f"Pre-configuration: {module.preconditions}")
                if module.compliance_mapping:
                    description_parts.append(f"Compliance: {module.compliance_mapping}")
                module.description = "\n".join(description_parts) if description_parts else None

                schema = get_parameter_schema_for_category(module.category)
                module.parameter_schema = schema or None

                module.checksum = _checksum_from_row(row)

                session.flush()  # ensure module.id populated before tenant links
                _ensure_tenant_links(session, module, module.enabled)

                if created:
                    stats["created"] += 1
                else:
                    stats["updated"] += 1

            if stats["rows"] == 0:
                raise ValueError("CSV contains no data rows")

            if dry_run:
                session.rollback()
            else:
                session.commit()
            return stats
        finally:
            session.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import Tenantra modules from CSV")
    parser.add_argument("csv", type=Path, help="Path to Tenantra_Scanning_Module_Table_v2_UPDATED.csv")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate without committing changes")
    args = parser.parse_args()

    stats = import_modules(args.csv, dry_run=args.dry_run)
    print(
        f"Processed {stats['rows']} rows (created={stats['created']}, updated={stats['updated']})"
    )


if __name__ == "__main__":
    main()
