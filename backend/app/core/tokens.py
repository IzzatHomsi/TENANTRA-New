import os
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Tuple
from fastapi import HTTPException, status

from sqlalchemy.orm import Session
from app.models.refresh_token import RefreshToken
from app.models.user import User

REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "14"))
REFRESH_IN_COOKIE = os.getenv("REFRESH_IN_COOKIE", "false").lower() in ("1","true","yes")

def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

def issue_refresh_token(db: Session, user: User, *, user_agent: Optional[str], ip: Optional[str]) -> str:
    raw = secrets.token_urlsafe(48)  # opaque ~384 bits
    tok = RefreshToken(
        user_id=user.id,
        token_hash=_hash_token(raw),
        created_at=datetime.utcnow(),
        expires_at=datetime.utcnow() + timedelta(days=REFRESH_EXPIRE_DAYS),
        user_agent=user_agent,
        ip=ip,
    )
    db.add(tok)
    db.commit()
    return raw

def rotate_refresh_token(db: Session, raw: str) -> Tuple[User, str]:
    tok = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_token(raw)).first()
    if not tok or tok.revoked_at or tok.expires_at < datetime.utcnow():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")
    user = db.query(User).filter(User.id == tok.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")
    # Revoke old and issue new
    tok.revoked_at = datetime.utcnow()
    db.commit()
    new_raw = issue_refresh_token(db, user, user_agent=tok.user_agent, ip=tok.ip)
    return user, new_raw

def revoke_refresh_token(db: Session, raw: str) -> None:
    tok = db.query(RefreshToken).filter(RefreshToken.token_hash == _hash_token(raw)).first()
    if tok and not tok.revoked_at:
        tok.revoked_at = datetime.utcnow()
        db.commit()

def revoke_all_for_user(db: Session, user_id: int) -> int:
    q = db.query(RefreshToken).filter(
        RefreshToken.user_id == user_id,
        RefreshToken.revoked_at.is_(None)
    )
    count = 0
    for t in q.all():
        t.revoked_at = datetime.utcnow()
        count += 1
    if count:
        db.commit()
    return count
