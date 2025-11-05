from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import os

from app.core.auth import get_admin_user
from app.database import get_db
from app.models.user import User

router = APIRouter(prefix="/admin/app", tags=["Admin App Logs"])


@router.get("/logs", response_model=dict)
def read_logs(db: Session = Depends(get_db), _: User = Depends(get_admin_user)) -> dict:
    path = os.getenv("LOG_FILE_PATH", "logs/tenantra_backend.log")
    p = Path(path)
    if not p.exists():
        raise HTTPException(status_code=404, detail="Log file not found")
    try:
        lines = p.read_text(encoding="utf-8", errors="ignore").splitlines()
        tail = lines[-500:]
        return {"path": str(p), "lines": tail}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

