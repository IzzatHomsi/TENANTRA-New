from typing import Dict
import os
from urllib.parse import urlparse
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.app_setting import AppSetting

router = APIRouter(prefix="/support/settings/public", tags=["Public Settings"])

WHITELIST_KEYS = {
    'theme.colors.primary',
    'grafana.url',
    'grafana.dashboard_uid',
    'grafana.datasource_uid',
}


@router.get("", response_model=Dict[str, object])
def get_public_settings(db: Session = Depends(get_db)) -> Dict[str, object]:
    out: Dict[str, object] = {}
    rows = (
        db.query(AppSetting)
        .filter(AppSetting.tenant_id.is_(None))
        .filter(AppSetting.key.in_(list(WHITELIST_KEYS)))
        .all()
    )
    for r in rows:
        val = r.value
        # Map internal service Grafana URL to same-origin subpath for browser embedding
        if r.key == 'grafana.url' and isinstance(val, str):
            try:
                u = urlparse(val)
                if u.hostname in {'grafana', 'grafana.local'} or (u.hostname in {'localhost','127.0.0.1'} and u.port == 3000):
                    # Prefer proxied subpath which we expose at /grafana/
                    val = '/grafana'
            except Exception:
                pass
        out[r.key] = val
    return out
