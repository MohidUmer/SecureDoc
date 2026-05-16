"""
Structured audit logging to database.

Security:
- Never log passwords, tokens, or file contents.
- Suitable for admin review and incident traceability.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from securedoc.extensions import db
from securedoc.models.audit_log import AuditLog

if TYPE_CHECKING:
    from flask import Request


def log_event(
    event_type: str,
    message: str,
    *,
    user_id: int | None = None,
    request: "Request | None" = None,
    extra: str | None = None,
) -> None:
    """
    Persist one audit row.

    :param event_type: Short category e.g. AUTH_SUCCESS, DOCUMENT_UPLOAD.
    :param message: Human-readable description without secrets.
    :param user_id: Acting user if known.
    :param request: Optional Flask request for client IP.
    :param extra: Non-sensitive contextual string (document id, etc.).
    """
    ip = request.remote_addr if request else None
    row = AuditLog(
        event_type=event_type[:64],
        message=message[:512],
        user_id=user_id,
        ip_address=(ip[:45] if ip else None),
        extra=(extra[:512] if extra else None),
    )
    db.session.add(row)
