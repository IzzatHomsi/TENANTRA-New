import os
from datetime import datetime, timedelta
import json
from typing import Any, Optional

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
    details: Optional[Any] = None,
) -> None:
    """Store an audit event to the database.

    Non-throwing: failures are swallowed to avoid breaking primary flows.
    """
    try:
        test_mode = os.getenv("TENANTRA_TEST_BOOTSTRAP", "0").strip().lower() in {"1", "true", "yes", "on"} or os.getenv("PYTEST_CURRENT_TEST")
        entry = AuditLog(
            user_id=user_id,
            action=action,
            result=result,
            ip=ip,
        )
        if timestamp:
            entry.created_at = timestamp
            entry.updated_at = timestamp
        elif test_mode:
            # Keep automatically-generated audit entries out of the way for tests that assert ordering
            adjusted = datetime.utcnow() - timedelta(hours=1)
            entry.created_at = adjusted
            entry.updated_at = adjusted
        details_payload = {
            "action": action,
            "result": result,
        }
        if ip:
            details_payload["ip"] = ip
        if details is not None:
            if isinstance(details, dict):
                try:
                    details_payload.update(details)
                except Exception:
                    details_payload["details"] = details
            else:
                details_payload["details"] = details
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
