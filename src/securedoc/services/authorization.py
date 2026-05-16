"""
Central authorization for document operations (RBAC + ownership).

Security:
- Call from every route that reads or mutates document data (prevent IDOR).
- Owner has full access; grantee access depends on ShareRole.
"""
from __future__ import annotations

from enum import Enum

from securedoc.extensions import db
from securedoc.models.document import Document
from securedoc.models.share import Share, ShareRole
from securedoc.models.user import User


class DocumentAction(str, Enum):
    VIEW = "VIEW"
    DOWNLOAD = "DOWNLOAD"
    COMMENT = "COMMENT"
    EDIT = "EDIT"
    SHARE = "SHARE"
    DELETE = "DELETE"


def _role_allows(role: ShareRole, action: DocumentAction) -> bool:
    """Grantee permissions only (not owner). SHARE/DELETE never use this for grantee."""
    if action in (DocumentAction.VIEW, DocumentAction.DOWNLOAD):
        return True
    if action == DocumentAction.COMMENT:
        return role in (ShareRole.COMMENT, ShareRole.EDIT)
    if action == DocumentAction.EDIT:
        return role is ShareRole.EDIT
    return False


def get_effective_role(user: User, document: Document) -> ShareRole | None:
    """Owner treated as full control; else explicit share role."""
    if document.owner_id == user.id:
        return ShareRole.EDIT
    share = Share.query.filter_by(
        document_id=document.id,
        grantee_id=user.id,
    ).first()
    if not share:
        return None
    try:
        return ShareRole(share.role)
    except ValueError:
        return None


def authorize(user: User, document: Document, action: DocumentAction) -> bool:
    """
    Return True if user may perform action on document.

    :param user: Authenticated user.
    :param document: Target document row.
    :param action: Verb being attempted.
    """
    if document.owner_id == user.id:
        return True
    share = Share.query.filter_by(
        document_id=document.id,
        grantee_id=user.id,
    ).first()
    if share is None:
        return False
    if action in (DocumentAction.SHARE, DocumentAction.DELETE):
        return False
    try:
        role = ShareRole(share.role)
    except ValueError:
        return False
    return _role_allows(role, action)


def authorize_by_id(user: User, document_id: int, action: DocumentAction) -> Document | None:
    """
    Load document by id and authorize; returns Document if allowed else None.

    Security: use this helper to avoid forgetting authz after query.
    """
    doc = db.session.get(Document, document_id)
    if doc is None:
        return None
    if authorize(user, doc, action):
        return doc
    return None
