"""
Append-style security audit events (no secrets / no file content).

Security: queryable by admin only; do not store passwords or ciphertext.
"""
from __future__ import annotations

from datetime import datetime, timezone

from securedoc.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(64), nullable=False, index=True)
    message = db.Column(db.String(512), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    extra = db.Column(db.String(512), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
