"""
Password hashing using bcrypt (assignment requirement: bcrypt/argon2 preferred).

Security: never log plaintext passwords; use check_password for login only.
"""
from __future__ import annotations

import bcrypt


def hash_password(plain: str) -> str:
    """Hash password for storage (UTF-8 safe)."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(plain.encode("utf-8"), salt).decode("ascii")


def check_password(plain: str, password_hash: str) -> bool:
    """Constant-time verify against stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain.encode("utf-8"),
            password_hash.encode("ascii"),
        )
    except (ValueError, TypeError):
        return False
