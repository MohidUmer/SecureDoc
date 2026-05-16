"""Authorization smoke tests (IDOR / role boundaries)."""
from __future__ import annotations

from securedoc.extensions import db
from securedoc.models.document import Document
from securedoc.models.share import Share
from securedoc.models.user import User
from securedoc.utils.passwords import hash_password


def _login(client, username: str, password: str = "password12") -> None:
    client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
            "submit": "Login",
        },
        follow_redirects=True,
    )


def test_non_owner_cannot_delete_document(client, app):
    with app.app_context():
        alice = User(
            username="alice",
            email="alice@example.com",
            password_hash=hash_password("password12"),
        )
        bob = User(
            username="bob",
            email="bob@example.com",
            password_hash=hash_password("password12"),
        )
        db.session.add_all([alice, bob])
        db.session.commit()
        doc = Document(
            owner_id=alice.id,
            title="secret.txt",
            stored_filename="dummy",
            mime_type="text/plain",
            size_bytes=1,
            content_sha256="0" * 64,
        )
        db.session.add(doc)
        db.session.commit()
        doc_id = doc.id

    _login(client, "bob")
    resp = client.post(f"/documents/{doc_id}/delete", data={})
    assert resp.status_code == 404


def test_view_grantee_cannot_share(client, app):
    with app.app_context():
        owner = User(
            username="owner2",
            email="owner2@example.com",
            password_hash=hash_password("password12"),
        )
        grantee = User(
            username="grantee2",
            email="grantee2@example.com",
            password_hash=hash_password("password12"),
        )
        db.session.add_all([owner, grantee])
        db.session.commit()
        doc = Document(
            owner_id=owner.id,
            title="shared.pdf",
            stored_filename="dummy2",
            mime_type="application/pdf",
            size_bytes=1,
            content_sha256="1" * 64,
        )
        db.session.add(doc)
        db.session.flush()
        db.session.add(
            Share(document_id=doc.id, grantee_id=grantee.id, role="VIEW"),
        )
        db.session.commit()
        doc_id = doc.id

    _login(client, "grantee2")
    resp = client.post(
        f"/documents/{doc_id}/share",
        data={
            "grantee_username": "owner2",
            "role": "VIEW",
            "submit": "Share",
        },
        follow_redirects=False,
    )
    assert resp.status_code == 404


def test_admin_audit_forbidden_for_normal_user(client, app):
    with app.app_context():
        u = User(
            username="norm",
            email="norm@example.com",
            password_hash=hash_password("password12"),
            is_admin=False,
        )
        db.session.add(u)
        db.session.commit()

    _login(client, "norm")
    resp = client.get("/admin/audit")
    assert resp.status_code == 403
