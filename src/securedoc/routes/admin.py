"""
Admin-only audit log viewer.

Security: requires is_admin; no sensitive payloads in list view.
"""
from __future__ import annotations

from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from securedoc.models.audit_log import AuditLog

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/audit")
@login_required
def audit_log():
    if not current_user.is_admin:
        abort(403)
    rows = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(500).all()
    return render_template("admin_audit.html", rows=rows)
