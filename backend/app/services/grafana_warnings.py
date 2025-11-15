from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Dict, List

_MAX_WARNINGS = 50
_WARNINGS: Deque[Dict[str, object]] = deque(maxlen=_MAX_WARNINGS)
_LOCK = threading.Lock()


def _derive_tag(message: str | None, body: str | None) -> str:
    haystack = f"{message or ''} {body or ''}".lower()
    if "loaddashboardscene" in haystack:
        return "grafana.loadDashboardScene"
    if "cannot unmarshal number" in haystack and "metricrequest.from" in haystack:
        return "grafana.timestamp"
    return "grafana.proxy"


def record_grafana_warning(*, status: int, path: str, method: str, message: str | None = None, body: str | None = None) -> None:
    payload = {
        "status": status,
        "path": path,
        "method": method,
        "message": message,
        "body": (body or "")[:200],
        "tag": _derive_tag(message, body),
        "timestamp": time.time(),
    }
    with _LOCK:
        _WARNINGS.appendleft(payload)


def list_grafana_warnings(limit: int = 20) -> List[Dict[str, object]]:
    with _LOCK:
        items = list(_WARNINGS)
    return items[:limit] if limit else items
