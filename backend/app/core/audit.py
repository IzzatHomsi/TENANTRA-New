# audit.py — structured audit logging for Tenantra
import json, logging, time
from typing import Any, Dict, Optional

_audit = logging.getLogger("tenantra.audit")

def log_audit(event: str, actor_id: str, actor_name: str, tenant: str, **extra: Any) -> None:
    """Emit a structured audit log line as JSON on logger 'tenantra.audit'."""
    payload: Dict[str, Any] = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "event": event,
        "actor_id": actor_id,
        "actor_name": actor_name,
        "tenant": tenant,
        **extra
    }
    try:
        _audit.info(json.dumps(payload, separators=(",", ":"), ensure_ascii=False))
    except Exception as e:
        _audit.error("audit_log_error:%s", str(e))
