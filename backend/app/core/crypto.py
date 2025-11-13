import base64
import hashlib
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def encrypt_data(raw: str, key: bytes) -> str:
    # Derive a 256-bit key from the provided bytes
    k = hashlib.sha256(key).digest()
    nonce = os.urandom(12)
    aesgcm = AESGCM(k)
    ct = aesgcm.encrypt(nonce, raw.encode("utf-8"), associated_data=None)
    return base64.b64encode(nonce + ct).decode("utf-8")


def decrypt_data(enc: str, key: bytes) -> str:
    try:
        data = base64.b64decode(enc)
        nonce, ct = data[:12], data[12:]
        k = hashlib.sha256(key).digest()
        aesgcm = AESGCM(k)
        pt = aesgcm.decrypt(nonce, ct, associated_data=None)
        return pt.decode("utf-8")
    except Exception as exc:  # pragma: no cover - defensive path
        raise ValueError("Failed to decrypt payload") from exc
