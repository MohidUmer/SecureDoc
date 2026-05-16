"""
Document and version models — metadata for encrypted blobs.

Security: file bytes live on disk encrypted; DB holds owner, ACL via shares, IV metadata.
"""
from __future__ import annotations

from datetime import datetime, timezone

from securedoc.extensions import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(64), unique=True, nullable=False, index=True)
    mime_type = db.Column(db.String(128), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    content_sha256 = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    versions = db.relationship(
        "DocumentVersion",
        backref="document",
        lazy="dynamic",
        order_by="DocumentVersion.version_number",
    )


class DocumentVersion(db.Model):
    __tablename__ = "document_versions"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=False, index=True)
    version_number = db.Column(db.Integer, nullable=False)
    stored_filename = db.Column(db.String(64), unique=True, nullable=False)
    mime_type = db.Column(db.String(128), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    parent_version_id = db.Column(db.Integer, db.ForeignKey("document_versions.id"), nullable=True)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint("document_id", "version_number", name="uq_doc_version"),
    )
