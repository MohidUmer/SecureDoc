"""
Comments on documents — stored text must be escaped on output (XSS mitigation).
"""
from __future__ import annotations

from datetime import datetime, timezone

from securedoc.extensions import db


class Comment(db.Model):
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    body = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author = db.relationship("User", foreign_keys=[user_id])
    document = db.relationship("Document", backref=db.backref("comments", lazy="dynamic"))
