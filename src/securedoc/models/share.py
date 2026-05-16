"""
Share grants — RBAC for collaborators (View / Comment / Edit).

Security: enforced server-side in authorization service on every sensitive route.
"""
from __future__ import annotations

import enum
from datetime import datetime, timezone

from securedoc.extensions import db


class ShareRole(str, enum.Enum):
    VIEW = "VIEW"
    COMMENT = "COMMENT"
    EDIT = "EDIT"


class Share(db.Model):
    __tablename__ = "shares"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    grantee_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    document = db.relationship("Document", backref=db.backref("shares", lazy="dynamic"))
    grantee = db.relationship("User", foreign_keys=[grantee_id])

    __table_args__ = (
        db.UniqueConstraint("document_id", "grantee_id", name="uq_share_doc_grantee"),
    )
