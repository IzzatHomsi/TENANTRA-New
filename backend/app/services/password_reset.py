from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken
from app.models.user import User

RESET_TOKEN_TTL_MINUTES = int(os.getenv("TENANTRA_RESET_TOKEN_MINUTES", "30"))


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def issue_password_reset_token(
    db: Session,
    user: User,
    *,
    user_agent: str | None = None,
    ip: str | None = None,
) -> str:
    raw_token = secrets.token_urlsafe(32)
    token = PasswordResetToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES),
        user_agent=user_agent,
        ip=ip,
    )
    db.add(token)
    db.commit()
    return raw_token


def use_password_reset_token(db: Session, raw_token: str) -> PasswordResetToken:
    token_hash = _hash_token(raw_token)
    token = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash,
            PasswordResetToken.used_at.is_(None),
            PasswordResetToken.expires_at >= datetime.utcnow(),
        )
        .first()
    )
    if not token:
        raise ValueError("Invalid or expired password reset token.")
    token.used_at = datetime.utcnow()
    db.add(token)
    db.commit()
    db.refresh(token)
    return token
