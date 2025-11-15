from __future__ import annotations

import hashlib
import os
import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.email_verification_token import EmailVerificationToken
from app.models.user import User

VERIFY_TOKEN_TTL_HOURS = int(os.getenv("TENANTRA_VERIFY_TOKEN_HOURS", "48"))


def _hash_token(raw: str) -> str:
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def issue_verification_token(
    db: Session,
    user: User,
    *,
    user_agent: str | None = None,
    ip: str | None = None,
) -> str:
    db.query(EmailVerificationToken).filter(
        EmailVerificationToken.user_id == user.id,
        EmailVerificationToken.used_at.is_(None),
    ).delete(synchronize_session=False)
    raw_token = secrets.token_urlsafe(32)
    token = EmailVerificationToken(
        user_id=user.id,
        token_hash=_hash_token(raw_token),
        expires_at=datetime.utcnow() + timedelta(hours=VERIFY_TOKEN_TTL_HOURS),
        user_agent=user_agent,
        ip=ip,
    )
    db.add(token)
    db.commit()
    return raw_token


def use_verification_token(db: Session, raw_token: str) -> EmailVerificationToken:
    token_hash = _hash_token(raw_token)
    token = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.token_hash == token_hash,
            EmailVerificationToken.used_at.is_(None),
            EmailVerificationToken.expires_at >= datetime.utcnow(),
        )
        .first()
    )
    if not token:
        raise ValueError("Invalid or expired verification token.")
    token.used_at = datetime.utcnow()
    db.add(token)
    db.commit()
    db.refresh(token)
    return token
