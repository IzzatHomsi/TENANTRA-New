"""Endpoints for registry and boot integrity monitoring."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.database import get_db
from app.models.agent import Agent
from app.models.boot_config import BootConfig
from app.models.integrity_event import IntegrityEvent
from app.models.registry_snapshot import RegistrySnapshot
from app.models.task_snapshot import TaskSnapshot
from app.models.service_baseline import ServiceBaseline
from app.models.service_snapshot import ServiceSnapshot
from app.models.user import User
from app.models.notification import Notification
from app.models.app_setting import AppSetting
from app.models.registry_baseline import RegistryBaseline
from app.models.task_baseline import TaskBaseline
from app.schemas.integrity import (
    BootConfigCreate,
    BootConfigRead,
    IntegrityEventCreate,
    IntegrityEventRead,
    RegistryDriftResponse,
    RegistrySnapshotCreate,
    RegistrySnapshotRead,
)
from app.schemas.persistence import (
    ServiceSnapshotCreate,
    ServiceSnapshotRead,
    TaskSnapshotCreate,
    TaskSnapshotRead,
)

router = APIRouter(prefix="/integrity", tags=["Integrity"])


def _resolve_tenant_id(current_user: User, tenant_id: Optional[int]) -> int:
    if current_user.tenant_id is not None:
        if tenant_id is not None and tenant_id != current_user.tenant_id:
            raise HTTPException(status_code=403, detail="Forbidden tenant scope")
        return current_user.tenant_id
    if tenant_id is None:
        raise HTTPException(status_code=400, detail="tenant_id is required for super administrators")
    return tenant_id


def _validate_agent(db: Session, agent_id: int, tenant_id: int) -> Agent:
    agent = db.query(Agent).filter(Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent {agent_id} not found")
    if agent.tenant_id and agent.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Agent does not belong to tenant")
    return agent


def _resolve_alert_recipients(db: Session, tenant_id: int) -> list[str]:
    recipients: list[str] = []
    try:
        rows = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == tenant_id, AppSetting.key == "integrity.alert.email.to")
            .all()
        )
        for r in rows:
            v = r.value
            if isinstance(v, list):
                recipients.extend([str(x) for x in v])
            elif isinstance(v, str):
                recipients.append(v)
    except Exception:
        pass
    if not recipients:
        try:
            admins = (
                db.query(User)
                .filter(User.tenant_id == tenant_id)
                .filter((User.role == "admin") | (User.role == "administrator"))
                .all()
            )
            for u in admins:
                mail = getattr(u, "email", None)
                if mail and "@" in mail:
                    recipients.append(mail)
        except Exception:
            pass
    if not recipients:
        recipients = ["admin@example.com"]
    recipients = [r for r in recipients if isinstance(r, str) and "@" in r]
    return recipients


@router.get("/registry", response_model=List[RegistrySnapshotRead])
def list_registry_snapshots(
    agent_id: Optional[int] = Query(None, description="Filter by agent"),
    hive: Optional[str] = Query(None, description="Filter by registry hive"),
    key_path: Optional[str] = Query(None, description="Filter by registry key"),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RegistrySnapshotRead]:
    """Return registry snapshots scoped to the current tenant."""

    tenant_id = current_user.tenant_id
    query = db.query(RegistrySnapshot)
    if tenant_id is not None:
        query = query.filter(RegistrySnapshot.tenant_id == tenant_id)
    if agent_id is not None:
        query = query.filter(RegistrySnapshot.agent_id == agent_id)
    if hive:
        query = query.filter(RegistrySnapshot.hive == hive)
    if key_path:
        query = query.filter(RegistrySnapshot.key_path.like(f"{key_path}%"))
    results = (
        query.order_by(RegistrySnapshot.collected_at.desc())
        .limit(limit)
        .all()
    )
    return [RegistrySnapshotRead.from_orm(item) for item in results]


@router.post("/registry", response_model=List[RegistrySnapshotRead])
def ingest_registry_snapshots(
    payload: List[RegistrySnapshotCreate],
    tenant_id: Optional[int] = Query(None, description="Tenant scope for super admins"),
    full_sync: bool = Query(False, description="Indicates the payload represents a full hive snapshot"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[RegistrySnapshotRead]:
    """Persist registry snapshots and generate drift events."""

    resolved_tenant = _resolve_tenant_id(current_user, tenant_id)
    stored: List[RegistrySnapshot] = []
    # tenant-backed ignore prefixes (merge with env)
    tenant_ignore_prefixes: List[str] = []
    try:
        tsi = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == resolved_tenant, AppSetting.key == "integrity.registry.ignore_prefixes")
            .all()
        )
        for r in tsi:
            v = r.value
            if isinstance(v, list):
                tenant_ignore_prefixes.extend([str(x).lower() for x in v])
            elif isinstance(v, str):
                tenant_ignore_prefixes.extend([p.strip().lower() for p in v.split(",") if p.strip()])
    except Exception:
        pass

    # Optionally collect the universe of keys for full-sync detection.
    observed_identity = set()
    for entry in payload:
        _validate_agent(db, entry.agent_id, resolved_tenant)
        snapshot = RegistrySnapshot(
            tenant_id=resolved_tenant,
            agent_id=entry.agent_id,
            hive=entry.hive,
            key_path=entry.key_path,
            value_name=entry.value_name,
            value_data=entry.value_data,
            value_type=entry.value_type,
            collected_at=entry.collected_at or datetime.utcnow(),
            checksum=entry.checksum,
        )
        try:
            db.add(snapshot)
            db.flush()
        except IntegrityError:
            db.rollback()
            # Update existing snapshot with same identity and collected_at
            existing = (
                db.query(RegistrySnapshot)
                .filter(
                    RegistrySnapshot.agent_id == entry.agent_id,
                    RegistrySnapshot.hive == entry.hive,
                    RegistrySnapshot.key_path == entry.key_path,
                    RegistrySnapshot.value_name == entry.value_name,
                    RegistrySnapshot.collected_at == (entry.collected_at or snapshot.collected_at),
                )
                .first()
            )
            if existing:
                existing.value_data = entry.value_data
                existing.value_type = entry.value_type
                snapshot = existing
                db.flush()
            else:
                db.add(snapshot)
                db.flush()
        previous = (
            db.query(RegistrySnapshot)
            .filter(
                RegistrySnapshot.agent_id == entry.agent_id,
                RegistrySnapshot.hive == entry.hive,
                RegistrySnapshot.key_path == entry.key_path,
                RegistrySnapshot.value_name == entry.value_name,
            )
            .order_by(RegistrySnapshot.collected_at.desc())
            .first()
        )
        db.add(snapshot)
        db.flush()
        stored.append(snapshot)
        observed_identity.add((entry.agent_id, entry.hive, entry.key_path, entry.value_name))

        # Ignore noisy keys
        lowered = snapshot.key_path.lower()
        if any(lowered.startswith(pfx) for pfx in tenant_ignore_prefixes):
            continue

        # Determine if baseline marks this entry critical (agent-specific wins)
        baseline_row = (
            db.query(RegistryBaseline)
            .filter(RegistryBaseline.tenant_id == resolved_tenant,
                    RegistryBaseline.hive == entry.hive,
                    RegistryBaseline.key_path == entry.key_path,
                    RegistryBaseline.value_name == entry.value_name,
                    RegistryBaseline.agent_id == entry.agent_id)
            .first()
        ) or (
            db.query(RegistryBaseline)
            .filter(RegistryBaseline.tenant_id == resolved_tenant,
                    RegistryBaseline.hive == entry.hive,
                    RegistryBaseline.key_path == entry.key_path,
                    RegistryBaseline.value_name == entry.value_name,
                    RegistryBaseline.agent_id.is_(None))
            .first()
        )
        is_baseline_critical = bool(getattr(baseline_row, "is_critical", False))

        if previous is None:
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="registry_new",
                    severity=("critical" if is_baseline_critical else "medium"),
                    title=f"New registry value {entry.key_path}",
                    description=f"New registry value detected at {entry.key_path}",
                    reference_id=snapshot.id,
                    reference_type="registry",
                    metadata=snapshot.value_data,
                )
            )
            if is_baseline_critical:
                try:
                    for addr in _resolve_alert_recipients(db, resolved_tenant):
                        db.add(Notification(tenant_id=resolved_tenant, recipient_id=None, recipient_email=addr, title=f"Critical registry drift: {entry.key_path}", message="Baseline-critical registry change detected", status="queued", severity="critical"))
                except Exception:
                    pass
            try:
                from prometheus_client import Counter as _PC
                _DR = _PC("integrity_drift_events", "Integrity drift events", labelnames=("kind","severity"))
                _DR.labels("registry", "critical" if is_baseline_critical else "medium").inc()
            except Exception:
                pass
        elif previous.value_data != entry.value_data or previous.value_type != entry.value_type:
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="registry_change",
                    severity=("critical" if is_baseline_critical else "high"),
                    title=f"Registry drift detected at {entry.key_path}",
                    description="Registry value changed",
                    reference_id=snapshot.id,
                    reference_type="registry",
                    metadata=snapshot.value_data,
                )
            )
            if is_baseline_critical:
                try:
                    for addr in _resolve_alert_recipients(db, resolved_tenant):
                        db.add(Notification(tenant_id=resolved_tenant, recipient_id=None, recipient_email=addr, title=f"Critical registry drift: {entry.key_path}", message="Baseline-critical registry change detected", status="queued", severity="critical"))
                except Exception:
                    pass
            try:
                from prometheus_client import Counter as _PC
                _DR = _PC("integrity_drift_events", "Integrity drift events", labelnames=("kind","severity"))
                _DR.labels("registry", "critical" if is_baseline_critical else "high").inc()
            except Exception:
                pass

    if full_sync and payload:
        # Identify removed entries by comparing to last known set.
        agent_id = payload[0].agent_id
        hive = payload[0].hive
        existing = (
            db.query(RegistrySnapshot)
            .filter(
                RegistrySnapshot.agent_id == agent_id,
                RegistrySnapshot.hive == hive,
                RegistrySnapshot.tenant_id == resolved_tenant,
            )
            .with_entities(
                RegistrySnapshot.agent_id,
                RegistrySnapshot.hive,
                RegistrySnapshot.key_path,
                RegistrySnapshot.value_name,
                func.max(RegistrySnapshot.collected_at),
            )
            .group_by(
                RegistrySnapshot.agent_id,
                RegistrySnapshot.hive,
                RegistrySnapshot.key_path,
                RegistrySnapshot.value_name,
            )
            .all()
        )
        for agent_id, hive, key_path, value_name, _ in existing:
            identity = (agent_id, hive, key_path, value_name)
            if identity not in observed_identity:
                baseline_row = (
                    db.query(RegistryBaseline)
                    .filter(
                        RegistryBaseline.tenant_id == resolved_tenant,
                        RegistryBaseline.hive == hive,
                        RegistryBaseline.key_path == key_path,
                        RegistryBaseline.value_name == value_name,
                        RegistryBaseline.agent_id == agent_id,
                    )
                    .first()
                ) or (
                    db.query(RegistryBaseline)
                    .filter(
                        RegistryBaseline.tenant_id == resolved_tenant,
                        RegistryBaseline.hive == hive,
                        RegistryBaseline.key_path == key_path,
                        RegistryBaseline.value_name == value_name,
                        RegistryBaseline.agent_id.is_(None),
                    )
                    .first()
                )
                is_baseline_critical = bool(getattr(baseline_row, "is_critical", False))
                sev = "critical" if is_baseline_critical else "medium"
                db.add(
                    IntegrityEvent(
                        tenant_id=resolved_tenant,
                        agent_id=agent_id,
                        event_type="registry_removed",
                        severity=sev,
                        title=f"Registry value removed at {key_path}",
                        description="Registry value missing from full snapshot",
                        reference_type="registry",
                        metadata=f"{key_path}|{value_name}",
                    )
                )
                try:
                    from prometheus_client import Counter as _PC
                    _DR = _PC("integrity_drift_events", "Integrity drift events", labelnames=("kind","severity"))
                    _DR.labels("registry", sev).inc()
                except Exception:
                    pass
                if sev == "critical":
                    try:
                        recipients = []
                        for r in db.query(AppSetting).filter(AppSetting.tenant_id == resolved_tenant, AppSetting.key == "integrity.alert.email.to").all():
                            v = r.value
                            if isinstance(v, list):
                                recipients.extend([str(x) for x in v])
                            elif isinstance(v, str):
                                recipients.append(v)
                        if not recipients:
                            recipients = ["admin@example.com"]
                        for addr in recipients:
                            db.add(Notification(tenant_id=resolved_tenant, recipient_id=None, recipient_email=addr, title=f"Critical registry deletion: {key_path}", message="Baseline-critical registry removal detected", status="queued", severity="critical"))
                    except Exception:
                        pass

    # counters
    try:
        if stored:
            from prometheus_client import Counter as _C, Gauge as _G  # local import safe
            _REG_CNT = _C("integrity_ingested_rows", "Integrity rows ingested", labelnames=("kind",))
            _REG_CNT.labels("registry").inc(len(stored))
            _LAST = _G("integrity_last_ingest_timestamp", "Last ingest timestamp", labelnames=("kind",))
            _LAST.labels("registry").set(datetime.utcnow().timestamp())
    except Exception:
        pass
    db.commit()
    return [RegistrySnapshotRead.from_orm(item) for item in stored]


@router.get("/registry/drift", response_model=RegistryDriftResponse)
def registry_drift_summary(
    agent_id: int = Query(..., description="Agent identifier"),
    hive: str = Query(..., description="Registry hive"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> RegistryDriftResponse:
    """Summarise drift for the latest registry collection."""

    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    _validate_agent(db, agent_id, tenant_id)

    latest_collections = (
        db.query(RegistrySnapshot)
        .filter(
            RegistrySnapshot.agent_id == agent_id,
            RegistrySnapshot.hive == hive,
            RegistrySnapshot.tenant_id == tenant_id,
        )
        .order_by(RegistrySnapshot.collected_at.desc())
        .limit(500)
        .all()
    )
    new_entries: List[RegistrySnapshotRead] = []
    modified_entries: List[RegistrySnapshotRead] = []
    removed_entries: List[RegistrySnapshotRead] = []

    seen = {}
    for snapshot in latest_collections:
        key = (snapshot.key_path, snapshot.value_name)
        if key not in seen:
            previous = (
                db.query(RegistrySnapshot)
                .filter(
                    RegistrySnapshot.agent_id == agent_id,
                    RegistrySnapshot.hive == hive,
                    RegistrySnapshot.key_path == snapshot.key_path,
                    RegistrySnapshot.value_name == snapshot.value_name,
                    RegistrySnapshot.collected_at < snapshot.collected_at,
                )
                .order_by(RegistrySnapshot.collected_at.desc())
                .first()
            )
            seen[key] = True
            if previous is None:
                new_entries.append(RegistrySnapshotRead.from_orm(snapshot))
            elif previous.value_data != snapshot.value_data:
                modified_entries.append(RegistrySnapshotRead.from_orm(snapshot))

    # Determine removed entries by looking at the latest snapshot set vs. previous.
    latest_keys = {
        (snap.key_path, snap.value_name)
        for snap in latest_collections
    }
    if latest_collections:
        reference_time = latest_collections[0].collected_at
        previous_keys = {
            (snap.key_path, snap.value_name)
            for snap in db.query(RegistrySnapshot)
            .filter(
                RegistrySnapshot.agent_id == agent_id,
                RegistrySnapshot.hive == hive,
                RegistrySnapshot.tenant_id == tenant_id,
                RegistrySnapshot.collected_at < reference_time,
            )
            .with_entities(RegistrySnapshot.key_path, RegistrySnapshot.value_name)
            .all()
        }
        removed = previous_keys - latest_keys
        for key_path, value_name in removed:
            placeholder = RegistrySnapshotRead(
                id=0,
                tenant_id=tenant_id,
                agent_id=agent_id,
                hive=hive,
                key_path=key_path,
                value_name=value_name,
                value_data=None,
                value_type=None,
                checksum=None,
                collected_at=reference_time,
            )
            removed_entries.append(placeholder)

    return RegistryDriftResponse(
        new_entries=new_entries,
        modified_entries=modified_entries,
        removed_entries=removed_entries,
    )


@router.get("/boot", response_model=List[BootConfigRead])
def list_boot_configs(
    agent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[BootConfigRead]:
    tenant_id = current_user.tenant_id
    query = db.query(BootConfig)
    if tenant_id is not None:
        query = query.filter(BootConfig.tenant_id == tenant_id)
    if agent_id is not None:
        query = query.filter(BootConfig.agent_id == agent_id)
    configs = query.order_by(BootConfig.collected_at.desc()).all()
    return [BootConfigRead.from_orm(cfg) for cfg in configs]


@router.post("/boot", response_model=BootConfigRead)
def ingest_boot_config(
    payload: BootConfigCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> BootConfigRead:
    resolved_tenant = _resolve_tenant_id(current_user, tenant_id)
    _validate_agent(db, payload.agent_id, resolved_tenant)

    boot_config = BootConfig(
        tenant_id=resolved_tenant,
        agent_id=payload.agent_id,
        platform=payload.platform,
        config_path=payload.config_path,
        content=payload.content,
        checksum=payload.checksum,
        collected_at=payload.collected_at or datetime.utcnow(),
    )
    previous = (
        db.query(BootConfig)
        .filter(
            BootConfig.tenant_id == resolved_tenant,
            BootConfig.agent_id == payload.agent_id,
            BootConfig.config_path == payload.config_path,
        )
        .order_by(BootConfig.collected_at.desc())
        .first()
    )
    db.add(boot_config)
    db.flush()
    if previous is None or previous.checksum != boot_config.checksum:
        db.add(
            IntegrityEvent(
                tenant_id=resolved_tenant,
                agent_id=payload.agent_id,
                event_type="boot_change",
                severity="high",
                title=f"Boot config change at {payload.config_path}",
                description="Boot configuration checksum changed",
                reference_id=boot_config.id,
                reference_type="boot",
            )
        )
    # counters
    try:
        from prometheus_client import Counter as _C, Gauge as _G
        _CNT = _C("integrity_ingested_rows", "Integrity rows ingested", labelnames=("kind",))
        _CNT.labels("boot").inc(1)
        _LAST = _G("integrity_last_ingest_timestamp", "Last ingest timestamp", labelnames=("kind",))
        _LAST.labels("boot").set(datetime.utcnow().timestamp())
    except Exception:
        pass
    db.commit()
    db.refresh(boot_config)
    return BootConfigRead.from_orm(boot_config)


@router.get("/events", response_model=List[IntegrityEventRead])
def list_integrity_events(
    agent_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(200, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[IntegrityEventRead]:
    tenant_id = current_user.tenant_id
    query = db.query(IntegrityEvent)
    if tenant_id is not None:
        query = query.filter(IntegrityEvent.tenant_id == tenant_id)
    if agent_id is not None:
        query = query.filter(IntegrityEvent.agent_id == agent_id)
    if event_type:
        query = query.filter(IntegrityEvent.event_type == event_type)
    if severity:
        query = query.filter(IntegrityEvent.severity == severity)
    events = query.order_by(IntegrityEvent.detected_at.desc()).limit(limit).all()
    return [IntegrityEventRead.from_orm(evt) for evt in events]


@router.post("/events", response_model=IntegrityEventRead)
def create_integrity_event(
    payload: IntegrityEventCreate,
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IntegrityEventRead:
    resolved_tenant = _resolve_tenant_id(current_user, tenant_id)
    if payload.agent_id:
        _validate_agent(db, payload.agent_id, resolved_tenant)
    event = IntegrityEvent(
        tenant_id=resolved_tenant,
        agent_id=payload.agent_id,
        event_type=payload.event_type,
        severity=payload.severity,
        title=payload.title,
        description=payload.description,
        reference_id=payload.reference_id,
        reference_type=payload.reference_type,
        metadata=payload.metadata,
        detected_at=payload.detected_at or datetime.utcnow(),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return IntegrityEventRead.from_orm(event)


@router.get("/registry/diff")
def registry_diff(
    agent_id: int = Query(...),
    hive: str = Query(...),
    left: str = Query(...),
    right: str = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    _validate_agent(db, agent_id, tenant_id)
    lt = datetime.fromisoformat(left)
    rt = datetime.fromisoformat(right)

    def latest_by_key(cutoff: datetime):
        rows = (
            db.query(RegistrySnapshot)
            .filter(RegistrySnapshot.tenant_id == tenant_id, RegistrySnapshot.agent_id == agent_id, RegistrySnapshot.hive == hive)
            .filter(RegistrySnapshot.collected_at <= cutoff)
            .order_by(RegistrySnapshot.collected_at.desc())
            .limit(2000)
            .all()
        )
        seen = {}
        for r in rows:
            key = (r.key_path, r.value_name)
            if key not in seen:
                seen[key] = r
        return seen

    L = latest_by_key(lt)
    R = latest_by_key(rt)
    added = [v.as_dict() for (k, v) in R.items() if k not in L]
    removed = [v.as_dict() for (k, v) in L.items() if k not in R]
    modified = []
    for k, rv in R.items():
        lv = L.get(k)
        if not lv:
            continue
        if (lv.value_data != rv.value_data) or (lv.value_type != rv.value_type):
            modified.append({
                "key": {"path": rv.key_path, "name": rv.value_name},
                "left": lv.as_dict(),
                "right": rv.as_dict(),
            })
    return {"added": added, "removed": removed, "modified": modified}


# --- Service and task snapshots are colocated here because they contribute
# --- to persistence integrity drift detection.


@router.get("/services", response_model=List[ServiceSnapshotRead])
def list_services(
    agent_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ServiceSnapshotRead]:
    tenant_id = current_user.tenant_id
    query = db.query(ServiceSnapshot)
    if tenant_id is not None:
        query = query.filter(ServiceSnapshot.tenant_id == tenant_id)
    if agent_id is not None:
        query = query.filter(ServiceSnapshot.agent_id == agent_id)
    if status:
        query = query.filter(ServiceSnapshot.status == status)
    results = query.order_by(ServiceSnapshot.collected_at.desc()).all()
    return [ServiceSnapshotRead.from_orm(row) for row in results]


@router.post("/services", response_model=List[ServiceSnapshotRead])
def ingest_services(
    payload: List[ServiceSnapshotCreate],
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[ServiceSnapshotRead]:
    resolved_tenant = _resolve_tenant_id(current_user, tenant_id)
    stored: List[ServiceSnapshot] = []
    # tenant-backed ignore names (merge with env)
    tenant_ignore_names: List[str] = []
    try:
        tsi = (
            db.query(AppSetting)
            .filter(AppSetting.tenant_id == resolved_tenant, AppSetting.key == "integrity.service.ignore_names")
            .all()
        )
        for r in tsi:
            v = r.value
            if isinstance(v, list):
                tenant_ignore_names.extend([str(x).lower() for x in v])
            elif isinstance(v, str):
                tenant_ignore_names.extend([p.strip().lower() for p in v.split(",") if p.strip()])
    except Exception:
        pass
    for entry in payload:
        _validate_agent(db, entry.agent_id, resolved_tenant)
        snapshot = ServiceSnapshot(
            tenant_id=resolved_tenant,
            agent_id=entry.agent_id,
            name=entry.name,
            display_name=entry.display_name,
            status=entry.status,
            start_mode=entry.start_mode,
            run_account=entry.run_account,
            binary_path=entry.binary_path,
            hash=entry.hash,
            collected_at=entry.collected_at or datetime.utcnow(),
        )
        previous = (
            db.query(ServiceSnapshot)
            .filter(
                ServiceSnapshot.tenant_id == resolved_tenant,
                ServiceSnapshot.agent_id == entry.agent_id,
                ServiceSnapshot.name == entry.name,
            )
            .order_by(ServiceSnapshot.collected_at.desc())
            .first()
        )
        db.add(snapshot)
        db.flush()
        stored.append(snapshot)
        # merge agent-specific ignores
        agent_ignores: List[str] = []
        try:
            key = f"integrity.service.ignore_names.agent.{entry.agent_id}"
            for r in db.query(AppSetting).filter(AppSetting.tenant_id == resolved_tenant, AppSetting.key == key).all():
                v = r.value
                if isinstance(v, list):
                    agent_ignores.extend([str(x).lower() for x in v])
                elif isinstance(v, str):
                    agent_ignores.extend([p.strip().lower() for p in v.split(",") if p.strip()])
        except Exception:
            pass

        if snapshot.name and (snapshot.name.lower() in tenant_ignore_names or snapshot.name.lower() in agent_ignores):
            continue
        if previous is None:
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="service_new",
                    severity="medium",
                    title=f"New service {entry.name}",
                    description=f"Service {entry.name} discovered",
                    reference_id=snapshot.id,
                    reference_type="service",
                )
            )
        elif previous.status != entry.status or previous.hash != entry.hash or previous.start_mode != entry.start_mode:
            severity = "medium"
            try:
                prev_mode = (previous.start_mode or "").strip().lower()
                new_mode = (entry.start_mode or "").strip().lower()
                if prev_mode == "disabled" and new_mode == "auto":
                    severity = "high"
            except Exception:
                pass
            try:
                bp = (entry.binary_path or "").lower()
                if bp.endswith(".sys") and (previous.hash != entry.hash or not entry.hash):
                    severity = "critical"
            except Exception:
                pass
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="service_change",
                    severity=severity,
                    title=f"Service change: {entry.name}",
                    description="Service configuration changed",
                    reference_id=snapshot.id,
                    reference_type="service",
                )
            )
            # alert on critical service drift
            if severity == "critical":
                try:
                    db.add(
                        Notification(
                            tenant_id=resolved_tenant,
                            recipient_id=None,
                            recipient_email="admin@example.com",
                            title=f"Critical service drift: {entry.name}",
                            message=f"Service {entry.name} drift detected on agent {entry.agent_id}",
                            status="queued",
                            severity="critical",
                        )
                    )
                except Exception:
                    pass
            try:
                from prometheus_client import Counter as _PC
                _DR = _PC("integrity_drift_events", "Integrity drift events", labelnames=("kind","severity"))
                _DR.labels("service", severity).inc()
            except Exception:
                pass
    # counters
    try:
        if stored:
            from prometheus_client import Counter as _C, Gauge as _G
            _CNT = _C("integrity_ingested_rows", "Integrity rows ingested", labelnames=("kind",))
            _CNT.labels("service").inc(len(stored))
            _LAST = _G("integrity_last_ingest_timestamp", "Last ingest timestamp", labelnames=("kind",))
            _LAST.labels("service").set(datetime.utcnow().timestamp())
    except Exception:
        pass
    db.commit()
    return [ServiceSnapshotRead.from_orm(item) for item in stored]


@router.get("/services/diff")
def services_diff(
    agent_id: int = Query(...),
    left: str = Query(..., description="Left timestamp (ISO)"),
    right: str = Query(..., description="Right timestamp (ISO)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    _validate_agent(db, agent_id, tenant_id)
    lt = datetime.fromisoformat(left)
    rt = datetime.fromisoformat(right)

    def latest_by_name(cutoff: datetime):
        rows = (
            db.query(ServiceSnapshot)
            .filter(ServiceSnapshot.tenant_id == tenant_id, ServiceSnapshot.agent_id == agent_id)
            .filter(ServiceSnapshot.collected_at <= cutoff)
            .order_by(ServiceSnapshot.collected_at.desc())
            .limit(1000)
            .all()
        )
        seen = {}
        for r in rows:
            if r.name not in seen:
                seen[r.name] = r
        return seen

    L = latest_by_name(lt)
    R = latest_by_name(rt)
    added = [v.as_dict() for (k, v) in R.items() if k not in L]
    removed = [v.as_dict() for (k, v) in L.items() if k not in R]
    changed = []
    for k, rv in R.items():
        lv = L.get(k)
        if not lv:
            continue
        if (lv.status != rv.status) or (lv.start_mode != rv.start_mode) or (lv.hash != rv.hash):
            changed.append({
                "name": k,
                "left": lv.as_dict(),
                "right": rv.as_dict(),
            })
    return {"added": added, "removed": removed, "changed": changed}


@router.get("/tasks", response_model=List[TaskSnapshotRead])
def list_tasks(
    agent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TaskSnapshotRead]:
    tenant_id = current_user.tenant_id
    query = db.query(TaskSnapshot)
    if tenant_id is not None:
        query = query.filter(TaskSnapshot.tenant_id == tenant_id)
    if agent_id is not None:
        query = query.filter(TaskSnapshot.agent_id == agent_id)
    tasks = query.order_by(TaskSnapshot.collected_at.desc()).all()
    return [TaskSnapshotRead.from_orm(task) for task in tasks]


@router.post("/tasks", response_model=List[TaskSnapshotRead])
def ingest_tasks(
    payload: List[TaskSnapshotCreate],
    tenant_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[TaskSnapshotRead]:
    resolved_tenant = _resolve_tenant_id(current_user, tenant_id)
    stored: List[TaskSnapshot] = []
    for entry in payload:
        _validate_agent(db, entry.agent_id, resolved_tenant)
        snapshot = TaskSnapshot(
            tenant_id=resolved_tenant,
            agent_id=entry.agent_id,
            name=entry.name,
            task_type=entry.task_type,
            schedule=entry.schedule,
            command=entry.command,
            last_run_time=entry.last_run_time,
            next_run_time=entry.next_run_time,
            status=entry.status,
            collected_at=entry.collected_at or datetime.utcnow(),
        )
        previous = (
            db.query(TaskSnapshot)
            .filter(
                TaskSnapshot.tenant_id == resolved_tenant,
                TaskSnapshot.agent_id == entry.agent_id,
                TaskSnapshot.name == entry.name,
            )
            .order_by(TaskSnapshot.collected_at.desc())
            .first()
        )
        db.add(snapshot)
        db.flush()
        stored.append(snapshot)
        if previous is None:
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="task_new",
                    severity="medium",
                    title=f"New scheduled task {entry.name}",
                    description="New persistence task discovered",
                    reference_id=snapshot.id,
                    reference_type="task",
                )
            )
        elif previous.command != entry.command or previous.schedule != entry.schedule:
            baseline_row = (
                db.query(TaskBaseline)
                .filter(TaskBaseline.tenant_id == resolved_tenant,
                        TaskBaseline.name == entry.name,
                        TaskBaseline.agent_id == entry.agent_id)
                .first()
            ) or (
                db.query(TaskBaseline)
                .filter(TaskBaseline.tenant_id == resolved_tenant,
                        TaskBaseline.name == entry.name,
                        TaskBaseline.agent_id.is_(None))
                .first()
            )
            sev = "critical" if getattr(baseline_row, "is_critical", False) else "medium"
            db.add(
                IntegrityEvent(
                    tenant_id=resolved_tenant,
                    agent_id=entry.agent_id,
                    event_type="task_change",
                    severity=sev,
                    title=f"Scheduled task modified {entry.name}",
                    description="Scheduled task configuration changed",
                    reference_id=snapshot.id,
                    reference_type="task",
                )
            )
    # counters
    try:
        if stored:
            from prometheus_client import Counter as _C
            _CNT = _C("integrity_ingested_rows", "Integrity rows ingested", labelnames=("kind",))
            _CNT.labels("task").inc(len(stored))
    except Exception:
        pass
    db.commit()
    return [TaskSnapshotRead.from_orm(item) for item in stored]


# --- Service baseline management ---


@router.get("/services/baseline", response_model=List[dict])
def get_service_baseline(
    agent_id: Optional[int] = Query(None, description="Agent scope; None returns tenant defaults"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    q = db.query(ServiceBaseline).filter(ServiceBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(ServiceBaseline.agent_id.is_(None))
    else:
        _validate_agent(db, agent_id, tenant_id)
        q = q.filter(ServiceBaseline.agent_id == agent_id)
    rows = q.order_by(ServiceBaseline.name.asc()).all()
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "name": r.name,
            "expected_status": r.expected_status,
            "expected_start_mode": r.expected_start_mode,
            "expected_hash": r.expected_hash,
            "expected_run_account": r.expected_run_account,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.post("/services/baseline", response_model=List[dict])
def upsert_service_baseline(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    agent_id = payload.get("agent_id")
    if agent_id is not None:
        _validate_agent(db, int(agent_id), tenant_id)

    entries = payload.get("entries") or []
    # replace scope
    q = db.query(ServiceBaseline).filter(ServiceBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(ServiceBaseline.agent_id.is_(None))
    else:
        q = q.filter(ServiceBaseline.agent_id == int(agent_id))
    q.delete(synchronize_session=False)

    created: List[ServiceBaseline] = []
    now = datetime.utcnow()
    for e in entries:
        row = ServiceBaseline(
            tenant_id=tenant_id,
            agent_id=int(agent_id) if agent_id is not None else None,
            name=e.get("name") or "",
            expected_status=e.get("expected_status"),
            expected_start_mode=e.get("expected_start_mode"),
            expected_hash=e.get("expected_hash"),
            expected_run_account=e.get("expected_run_account"),
            is_critical=bool(e.get("is_critical", False)),
            notes=e.get("notes"),
            created_at=now,
            updated_at=now,
        )
        if not row.name:
            continue
        db.add(row)
        created.append(row)
    db.commit()
    for r in created:
        db.refresh(r)
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "name": r.name,
            "expected_status": r.expected_status,
            "expected_start_mode": r.expected_start_mode,
            "expected_hash": r.expected_hash,
            "expected_run_account": r.expected_run_account,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in created
    ]


# --- Registry baseline management ---


@router.get("/registry/baseline", response_model=List[dict])
def get_registry_baseline(
    agent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    q = db.query(RegistryBaseline).filter(RegistryBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(RegistryBaseline.agent_id.is_(None))
    else:
        _validate_agent(db, agent_id, tenant_id)
        q = q.filter(RegistryBaseline.agent_id == agent_id)
    rows = q.order_by(RegistryBaseline.key_path.asc()).limit(1000).all()
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "hive": r.hive,
            "key_path": r.key_path,
            "value_name": r.value_name,
            "expected_value": r.expected_value,
            "expected_type": r.expected_type,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.post("/registry/baseline", response_model=List[dict])
def upsert_registry_baseline(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    agent_id = payload.get("agent_id")
    if agent_id is not None:
        _validate_agent(db, int(agent_id), tenant_id)

    entries = payload.get("entries") or []
    q = db.query(RegistryBaseline).filter(RegistryBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(RegistryBaseline.agent_id.is_(None))
    else:
        q = q.filter(RegistryBaseline.agent_id == int(agent_id))
    q.delete(synchronize_session=False)

    created: List[RegistryBaseline] = []
    now = datetime.utcnow()
    for e in entries:
        row = RegistryBaseline(
            tenant_id=tenant_id,
            agent_id=int(agent_id) if agent_id is not None else None,
            hive=e.get("hive") or "HKLM",
            key_path=e.get("key_path") or "",
            value_name=e.get("value_name"),
            expected_value=e.get("expected_value"),
            expected_type=e.get("expected_type"),
            is_critical=bool(e.get("is_critical", False)),
            notes=e.get("notes"),
            created_at=now,
            updated_at=now,
        )
        if not row.key_path:
            continue
        db.add(row)
        created.append(row)
    db.commit()
    for r in created:
        db.refresh(r)
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "hive": r.hive,
            "key_path": r.key_path,
            "value_name": r.value_name,
            "expected_value": r.expected_value,
            "expected_type": r.expected_type,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in created
    ]


# --- Task baseline management ---


@router.get("/tasks/baseline", response_model=List[dict])
def get_task_baseline(
    agent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    q = db.query(TaskBaseline).filter(TaskBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(TaskBaseline.agent_id.is_(None))
    else:
        _validate_agent(db, agent_id, tenant_id)
        q = q.filter(TaskBaseline.agent_id == agent_id)
    rows = q.order_by(TaskBaseline.name.asc()).limit(1000).all()
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "name": r.name,
            "task_type": r.task_type,
            "expected_schedule": r.expected_schedule,
            "expected_command": r.expected_command,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in rows
    ]


@router.post("/tasks/baseline", response_model=List[dict])
def upsert_task_baseline(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[dict]:
    tenant_id = _resolve_tenant_id(current_user, current_user.tenant_id)
    agent_id = payload.get("agent_id")
    if agent_id is not None:
        _validate_agent(db, int(agent_id), tenant_id)

    entries = payload.get("entries") or []
    q = db.query(TaskBaseline).filter(TaskBaseline.tenant_id == tenant_id)
    if agent_id is None:
        q = q.filter(TaskBaseline.agent_id.is_(None))
    else:
        q = q.filter(TaskBaseline.agent_id == int(agent_id))
    q.delete(synchronize_session=False)

    created: List[TaskBaseline] = []
    now = datetime.utcnow()
    for e in entries:
        row = TaskBaseline(
            tenant_id=tenant_id,
            agent_id=int(agent_id) if agent_id is not None else None,
            name=e.get("name") or "",
            task_type=e.get("task_type") or "",
            expected_schedule=e.get("expected_schedule"),
            expected_command=e.get("expected_command"),
            is_critical=bool(e.get("is_critical", False)),
            notes=e.get("notes"),
            created_at=now,
            updated_at=now,
        )
        if not row.name:
            continue
        db.add(row)
        created.append(row)
    db.commit()
    for r in created:
        db.refresh(r)
    return [
        {
            "id": r.id,
            "tenant_id": r.tenant_id,
            "agent_id": r.agent_id,
            "name": r.name,
            "task_type": r.task_type,
            "expected_schedule": r.expected_schedule,
            "expected_command": r.expected_command,
            "is_critical": r.is_critical,
            "notes": r.notes,
        }
        for r in created
    ]
