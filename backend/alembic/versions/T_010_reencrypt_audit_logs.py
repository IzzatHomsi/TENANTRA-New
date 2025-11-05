"""Re-encrypt legacy audit log payloads with the active encryption key."""

from __future__ import annotations

import base64
import json
from typing import Any, Dict

from alembic import op
import sqlalchemy as sa

try:
    # Import at module scope when available (runtime env)
    from app.core.crypto import decrypt_data, encrypt_data  # type: ignore
    from app.core.secrets import get_enc_key  # type: ignore
except Exception:  # pragma: no cover - allow alembic CLI to load heads without app package
    decrypt_data = None  # type: ignore
    encrypt_data = None  # type: ignore
    def get_enc_key():  # type: ignore
        return None

# Revision identifiers, used by Alembic.
revision = "T_010_reencrypt_audit_logs"
down_revision = "2f6b7a8c9d0e"
branch_labels = None
depends_on = None


audit_logs = sa.table(
    "audit_logs",
    sa.column("id", sa.Integer),
    sa.column("details", sa.String),
)


def _normalize_legacy_payload(value: str) -> Dict[str, Any]:
    candidate: Dict[str, Any] = {"raw": value}
    try:
        decoded = base64.b64decode(value)
        text = decoded.decode("utf-8", errors="ignore").strip()
        if text:
            candidate["decoded"] = text
    except Exception:
        candidate["decoded"] = None
    candidate["note"] = "Unable to decrypt with current key; preserving legacy payload"
    return candidate


def upgrade() -> None:
    bind = op.get_bind()
    # If crypto is unavailable (e.g., alembic heads in a minimal env), skip re-encryption
    if decrypt_data is None or encrypt_data is None:
        return
    key = get_enc_key()

    rows = list(bind.execute(sa.select(audit_logs.c.id, audit_logs.c.details)))
    for row in rows:
        stored = row.details
        if not stored:
            continue
        try:
            plaintext = decrypt_data(stored, key)  # type: ignore[misc]
        except Exception:
            legacy_payload = _normalize_legacy_payload(stored)
            plaintext = json.dumps(legacy_payload, ensure_ascii=False)
        transformed = encrypt_data(plaintext, key)  # type: ignore[misc]
        bind.execute(
            audit_logs.update()
            .where(audit_logs.c.id == row.id)
            .values(details=transformed)
        )


def downgrade() -> None:
    # Irreversible: legacy ciphertext is not recoverable once replaced.
    pass

