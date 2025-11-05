from datetime import datetime
import json
from typing import Optional

from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog
from app.observability.metrics import record_audit_write


def log_audit_event(
    db: Session,
    *,
    user_id: Optional[int],
    action: str,
    result: str,
    ip: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> None:
    """Store an audit event to the database.

    Non-throwing: failures are swallowed to avoid breaking primary flows.
    """
    try:
        entry = AuditLog(
            user_id=user_id,
            action=action,
            result=result,
            ip=ip,
        )
        if timestamp:
            entry.timestamp = timestamp
        details_payload = {
            "action": action,
            "result": result,
        }
        if ip:
            details_payload["ip"] = ip
        entry.details = json.dumps(details_payload)
        db.add(entry)
        db.commit()
        try:
            record_audit_write()
        except Exception:
            pass
    except Exception:
        try:
            db.rollback()
        except Exception:
            pass
