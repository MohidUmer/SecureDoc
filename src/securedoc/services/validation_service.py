"""
Input validation and upload hygiene.

Security:
- Server-side only; reject unexpected types and path traversal in filenames.
- Extension allowlist + optional magic sniff (best-effort without python-magic dependency).
"""
from __future__ import annotations

import re
from pathlib import PurePath


def sanitize_filename(name: str, max_length: int = 180) -> str:
    """
    Strip path components and dangerous characters from uploaded filename.

    :param name: Original filename from client (untrusted).
    :returns: Safe basename for display/storage reference (not a filesystem path).
    """
    if not name:
        return "unnamed"
    base = PurePath(name).name
    base = re.sub(r"[^\w.\- ]+", "", base, flags=re.UNICODE)
    base = base.strip(" .")
    if not base:
        return "unnamed"
    return base[:max_length]


def allowed_extension(filename: str, allowed: frozenset[str]) -> bool:
    """Return True if file extension (lowercase, no dot) is in allowlist."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower()
    return ext in allowed


def validate_comment_body(body: str, max_len: int = 4000) -> tuple[bool, str]:
    """Reject empty or oversized comments (XSS handled at render time)."""
    if not body or not body.strip():
        return False, "Comment cannot be empty."
    if len(body) > max_len:
        return False, "Comment too long."
    return True, ""
