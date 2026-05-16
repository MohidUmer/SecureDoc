"""
Symmetric encryption for document blobs at rest (Fernet / AES + HMAC).

Security:
- Uses ENCRYPTION_KEY from environment (32-byte url-safe base64 Fernet key).
- Unique Fernet token per encrypt call includes IV; suitable for per-file ciphertext.
- Does not store keys in the database alongside ciphertext (key is process env only).
"""
from __future__ import annotations

import hashlib
import os
from typing import BinaryIO

from cryptography.fernet import Fernet, InvalidToken


class CryptoService:
    """Encrypt/decrypt file payloads using application master key."""

    def __init__(self, key: str | None = None) -> None:
        raw = key or os.getenv("ENCRYPTION_KEY")
        if not raw:
            raise RuntimeError(
                "ENCRYPTION_KEY is not set. Generate with: "
                "python -c \"from cryptography.fernet import Fernet; "
                'print(Fernet.generate_key().decode())"'
            )
        self._fernet = Fernet(raw.encode() if isinstance(raw, str) else raw)

    def encrypt_bytes(self, data: bytes) -> bytes:
        """Encrypt plaintext bytes; returns token including IV and MAC."""
        return self._fernet.encrypt(data)

    def decrypt_bytes(self, token: bytes) -> bytes:
        """Decrypt ciphertext; raises InvalidToken on tampering."""
        return self._fernet.decrypt(token)

    def encrypt_stream(self, src: BinaryIO) -> bytes:
        """Read entire stream and encrypt (size-limited by caller)."""
        return self.encrypt_bytes(src.read())

    def sha256_hex(self, data: bytes) -> str:
        """Integrity helper for metadata (not a substitute for AEAD inside Fernet)."""
        return hashlib.sha256(data).hexdigest()


def get_crypto_service() -> CryptoService:
    """Factory for request-scoped or app-wide crypto."""
    return CryptoService()
