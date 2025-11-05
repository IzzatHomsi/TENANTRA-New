"""Backend log viewer API.

Provides administrative access to the backend log file.  The log file
path is configurable via the ``BACKEND_LOG_PATH`` environment
variable; by default it points to ``logs/tenantra_backend.log`` inside
the project root.  Responses are returned as structured JSON entries
with minimal parsing.  Only users with the ``admin`` or ``super_admin``
roles may access this endpoint.
"""

import os
import re
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.utils.rbac import role_required

router = APIRouter(tags=["Logs"])

DEFAULT_LOG_PATH = os.getenv(
    "BACKEND_LOG_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "..", "logs", "tenantra_backend.log"),
)

LOG_LINE_RE = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?)\s+(?P<level>[A-Z]+)\s+(?P<message>.*)$"
)


class LogEntry(BaseModel):
    timestamp: str
    level: str
    message: str
    raw: str


def _parse_log_line(line: str) -> LogEntry:
    text = line.rstrip("\n")
    match = LOG_LINE_RE.match(text)
    if match:
        ts = match.group("timestamp").replace(" ", "T", 1)
        ts = ts.replace(",", ".")
        return LogEntry(
            timestamp=ts,
            level=match.group("level"),
            message=match.group("message").strip(),
            raw=text,
        )
    return LogEntry(timestamp="", level="INFO", message=text, raw=text)


@router.get("/logs", response_model=List[LogEntry])
def view_logs(
    lines: int = Query(100, ge=1, le=10000, description="Number of log lines to return"),
    limit: Optional[int] = Query(None, ge=1, le=10000, description="Alias for 'lines' used by the frontend"),
    _: None = Depends(role_required("admin", "super_admin")),
):
    """Stream the last N lines of the backend log file.

    Administrators can specify the number of lines to retrieve.  If the
    log file does not exist a 404 is returned.  Reading is performed
    from the end of the file to avoid loading large files entirely
    into memory.
    """
    log_path = DEFAULT_LOG_PATH
    if not os.path.exists(log_path):
        raise HTTPException(status_code=404, detail="Log file not found")
    try:
        # Read the entire file then take the last ``lines`` lines
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            all_lines = f.readlines()
        requested = limit or lines
        tail = all_lines[-requested:]
        return [_parse_log_line(entry) for entry in tail]
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Unable to read log file") from exc
