"""
Public and dashboard routes.

Security: dashboard lists only documents the user may access (owner or shared).
"""
from __future__ import annotations

from flask import Blueprint, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from securedoc.extensions import db
from securedoc.models.document import Document
from securedoc.models.share import Share

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    return render_template("landing.html")


@main_bp.route("/dashboard", methods=["GET"])
@login_required
def dashboard():
    q = (request.args.get("q") or "").strip()[:200]

    owned = Document.query.filter_by(owner_id=current_user.id).order_by(
        Document.updated_at.desc()
    )
    if q:
        owned = owned.filter(Document.title.ilike(f"%{q}%"))

    shared_ids = (
        db.session.query(Share.document_id)
        .filter(Share.grantee_id == current_user.id)
        .subquery()
    )
    shared = Document.query.filter(Document.id.in_(db.session.query(shared_ids)))
    if q:
        shared = shared.filter(Document.title.ilike(f"%{q}%"))

    return render_template(
        "dashboard.html",
        owned_documents=owned.all(),
        shared_documents=shared.order_by(Document.updated_at.desc()).all(),
        query=q,
    )
