"""
Document CRUD: upload, download, share, comment, version, delete.

Security:
- Server-side authorization on every action (IDOR prevention).
- Encrypted storage; CSRF on POST; validated uploads.
"""
from __future__ import annotations

import secrets
from pathlib import Path

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from flask_login import current_user, login_required
from io import BytesIO
from werkzeug.utils import secure_filename

from securedoc.extensions import db
from securedoc.forms import CommentForm, DocumentUploadForm, ShareForm
from securedoc.models.comment import Comment
from securedoc.models.document import Document, DocumentVersion
from securedoc.models.share import Share, ShareRole
from securedoc.models.user import User
from securedoc.services.audit_service import log_event
from securedoc.services.authorization import DocumentAction, authorize, authorize_by_id
from cryptography.fernet import InvalidToken

from securedoc.services.crypto_service import get_crypto_service
from securedoc.services.validation_service import (
    allowed_extension,
    sanitize_filename,
    validate_comment_body,
)

documents_bp = Blueprint("documents", __name__)


def _storage_path(stored_filename: str) -> Path:
    base = Path(current_app.config["STORAGE_PATH"])
    return base / stored_filename


@documents_bp.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    form = DocumentUploadForm()
    if form.validate_on_submit():
        raw_name = form.file.data.filename or ""
        safe_display = sanitize_filename(raw_name)
        if not allowed_extension(
            safe_display,
            current_app.config["ALLOWED_UPLOAD_EXTENSIONS"],
        ):
            flash("File type not allowed.", "error")
            log_event(
                "UPLOAD_REJECT",
                f"Extension rejected: {safe_display}",
                user_id=current_user.id,
                request=request,
            )
            return render_template("upload.html", form=form)

        data = form.file.data.read()
        if not data:
            flash("Empty file.", "error")
            return render_template("upload.html", form=form)

        crypto = get_crypto_service()
        token = crypto.encrypt_bytes(data)
        digest = crypto.sha256_hex(data)

        stored_name = secrets.token_urlsafe(32)
        path = _storage_path(stored_name)
        path.write_bytes(token)

        doc = Document(
            owner_id=current_user.id,
            title=form.title.data.strip()[:255],
            stored_filename=stored_name,
            mime_type=form.file.data.mimetype or "application/octet-stream",
            size_bytes=len(data),
            content_sha256=digest,
        )
        db.session.add(doc)
        db.session.flush()
        ver = DocumentVersion(
            document_id=doc.id,
            version_number=1,
            stored_filename=stored_name,
            mime_type=doc.mime_type,
            size_bytes=doc.size_bytes,
            parent_version_id=None,
            created_by_id=current_user.id,
        )
        db.session.add(ver)
        db.session.commit()
        log_event(
            "DOCUMENT_UPLOAD",
            f"doc_id={doc.id}",
            user_id=current_user.id,
            request=request,
            extra=f"title={doc.title[:80]}",
        )
        flash("Document uploaded securely.", "success")
        return redirect(url_for("documents.detail", document_id=doc.id))

    return render_template("upload.html", form=form)


@documents_bp.route("/<int:document_id>", methods=["GET"])
@login_required
def detail(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.VIEW)
    if doc is None:
        abort(404)

    comment_form = CommentForm()
    share_form = ShareForm()

    versions = doc.versions.order_by(DocumentVersion.version_number.desc()).all()
    comments = doc.comments.order_by(Comment.created_at.asc()).all()
    can_dl = authorize(current_user, doc, DocumentAction.DOWNLOAD)
    can_share = authorize(current_user, doc, DocumentAction.SHARE)
    can_comment = authorize(current_user, doc, DocumentAction.COMMENT)
    can_edit = authorize(current_user, doc, DocumentAction.EDIT)
    can_delete = authorize(current_user, doc, DocumentAction.DELETE)

    return render_template(
        "document_detail.html",
        doc=doc,
        comment_form=comment_form,
        share_form=share_form,
        versions=versions,
        comments=comments,
        can_download=can_dl,
        can_share=can_share,
        can_comment=can_comment,
        can_edit=can_edit,
        can_delete=can_delete,
    )


@documents_bp.route("/<int:document_id>/comment", methods=["POST"])
@login_required
def add_comment(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.COMMENT)
    if doc is None:
        abort(404)
    form = CommentForm()
    if form.validate_on_submit():
        ok, msg = validate_comment_body(form.body.data)
        if not ok:
            flash(msg, "error")
        else:
            c = Comment(
                document_id=doc.id,
                user_id=current_user.id,
                body=form.body.data.strip()[:4000],
            )
            db.session.add(c)
            db.session.commit()
            log_event("COMMENT_ADD", f"doc_id={doc.id}", user_id=current_user.id, request=request)
            flash("Comment added.", "success")
    else:
        flash("Invalid comment.", "error")
    return redirect(url_for("documents.detail", document_id=doc.id))


@documents_bp.route("/<int:document_id>/share", methods=["POST"])
@login_required
def add_share(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.SHARE)
    if doc is None:
        abort(404)
    form = ShareForm()
    if form.validate_on_submit():
        uname = form.grantee_username.data.strip()
        grantee = User.query.filter_by(username=uname).first()
        if not grantee or grantee.id == current_user.id:
            flash("User not found.", "error")
        elif grantee.id == doc.owner_id:
            flash("Cannot share with owner.", "error")
        else:
            role = ShareRole[form.role.data]
            existing = Share.query.filter_by(
                document_id=doc.id,
                grantee_id=grantee.id,
            ).first()
            if existing:
                existing.role = role.value
            else:
                db.session.add(
                    Share(
                        document_id=doc.id,
                        grantee_id=grantee.id,
                        role=role.value,
                    )
                )
            db.session.commit()
            log_event(
                "SHARE_CHANGED",
                f"doc_id={doc.id} grantee={uname} role={role.value}",
                user_id=current_user.id,
                request=request,
            )
            flash("Sharing updated.", "success")
    else:
        flash("Invalid share form.", "error")
    return redirect(url_for("documents.detail", document_id=doc.id))


@documents_bp.route("/<int:document_id>/download")
@login_required
def download(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.DOWNLOAD)
    if doc is None:
        abort(404)
    path = _storage_path(doc.stored_filename)
    if not path.is_file():
        flash("File missing.", "error")
        abort(404)
    token = path.read_bytes()
    try:
        crypto = get_crypto_service()
        plain = crypto.decrypt_bytes(token)
    except InvalidToken:
        log_event("DECRYPT_FAIL", f"doc_id={doc.id}", user_id=current_user.id, request=request)
        flash("Could not decrypt file.", "error")
        return redirect(url_for("documents.detail", document_id=doc.id))

    log_event("DOCUMENT_DOWNLOAD", f"doc_id={doc.id}", user_id=current_user.id, request=request)
    fname = secure_filename(doc.title)[:80] or "document"
    ext = ""
    if "." in (doc.title or ""):
        ext = "." + doc.title.rsplit(".", 1)[-1][:10]
    return send_file(
        BytesIO(plain),
        as_attachment=True,
        download_name=f"{fname}{ext}" if ext else fname + ".bin",
        mimetype=doc.mime_type,
    )


@documents_bp.route("/<int:document_id>/version", methods=["POST"])
@login_required
def new_version(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.EDIT)
    if doc is None:
        abort(404)
    file = request.files.get("file")
    if not file or not file.filename:
        flash("No file.", "error")
        return redirect(url_for("documents.detail", document_id=doc.id))
    safe_display = sanitize_filename(file.filename)
    if not allowed_extension(
        safe_display,
        current_app.config["ALLOWED_UPLOAD_EXTENSIONS"],
    ):
        flash("File type not allowed.", "error")
        return redirect(url_for("documents.detail", document_id=doc.id))

    data = file.read()
    crypto = get_crypto_service()
    token = crypto.encrypt_bytes(data)
    stored_name = secrets.token_urlsafe(32)
    path = _storage_path(stored_name)
    path.write_bytes(token)

    last_ver = doc.versions.order_by(DocumentVersion.version_number.desc()).first()
    next_num = (last_ver.version_number + 1) if last_ver else 1

    ver = DocumentVersion(
        document_id=doc.id,
        version_number=next_num,
        stored_filename=stored_name,
        mime_type=file.mimetype or "application/octet-stream",
        size_bytes=len(data),
        parent_version_id=last_ver.id if last_ver else None,
        created_by_id=current_user.id,
    )
    doc.stored_filename = stored_name
    doc.mime_type = ver.mime_type
    doc.size_bytes = ver.size_bytes
    doc.content_sha256 = crypto.sha256_hex(data)
    db.session.add(ver)
    db.session.commit()
    log_event("VERSION_ADD", f"doc_id={doc.id} v={next_num}", user_id=current_user.id, request=request)
    flash("New version saved.", "success")
    return redirect(url_for("documents.detail", document_id=doc.id))


@documents_bp.route("/<int:document_id>/delete", methods=["POST"])
@login_required
def delete_document(document_id: int):
    doc = authorize_by_id(current_user, document_id, DocumentAction.DELETE)
    if doc is None:
        abort(404)
    for ver in doc.versions.all():
        p = _storage_path(ver.stored_filename)
        if p.is_file():
            p.unlink(missing_ok=True)
    Share.query.filter_by(document_id=doc.id).delete()
    Comment.query.filter_by(document_id=doc.id).delete()
    DocumentVersion.query.filter_by(document_id=doc.id).delete()
    db.session.delete(doc)
    db.session.commit()
    log_event("DOCUMENT_DELETE", f"doc_id={document_id}", user_id=current_user.id, request=request)
    flash("Document deleted.", "info")
    return redirect(url_for("main.dashboard"))
