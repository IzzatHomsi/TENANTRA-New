from __future__ import annotations

import logging
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.models.revoked_token import RevokedToken

logger = logging.getLogger("tenantra.token_blocklist")


def revoke_token(
    db: Session,
    *,
    user_id: int,
    jti: Optional[str],
    expires_at: Optional[datetime],
    reason: str = "logout",
) -> None:
    if not jti:
        return
    exists = (
        db.query(RevokedToken)
        .filter(RevokedToken.jti == jti)
        .first()
    )
    if exists:
        return
    db.add(
        RevokedToken(
            user_id=user_id,
            jti=jti,
            expires_at=expires_at,
            reason=reason,
        )
    )
    db.commit()


def revoke_tokens_issued_before(
    db: Session,
    *,
    user_id: int,
    cutoff: datetime,
    reason: str = "password_reset",
) -> None:
    db.add(
        RevokedToken(
            user_id=user_id,
            jti=None,
            revoked_at=cutoff,
            reason=reason,
        )
    )
    db.commit()


def is_token_revoked(
    db: Session,
    *,
    user_id: int,
    jti: Optional[str],
    issued_at: Optional[datetime],
) -> bool:
    if jti:
        exists = (
            db.query(RevokedToken)
            .filter(RevokedToken.jti == jti)
            .first()
        )
        if exists:
            logger.debug("token revoked via jti user_id=%s jti=%s", user_id, jti)
            return True
    if issued_at is not None:
        entry = (
            db.query(RevokedToken)
            .filter(RevokedToken.user_id == user_id, RevokedToken.jti.is_(None))
            .order_by(RevokedToken.revoked_at.desc())
            .first()
        )
        if entry and entry.revoked_at >= issued_at:
            logger.debug(
                "token revoked via cutoff user_id=%s issued_at=%s revoked_at=%s",
                user_id,
                issued_at.isoformat(),
                entry.revoked_at.isoformat() if entry.revoked_at else None,
            )
            return True
    return False
