"""
Authentication routes: register, login, logout.

Security:
- bcrypt password hashing; rate limits; optional account lockout after failures.
- Generic error on failed login (no user enumeration).
- Audit events without credentials.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import or_

from securedoc.extensions import db, limiter
from securedoc.forms import LoginForm, RegisterForm
from securedoc.models.user import User
from securedoc.services.audit_service import log_event
from securedoc.utils.passwords import check_password, hash_password

auth_bp = Blueprint("auth", __name__)

MAX_FAILED = 5
LOCK_MINUTES = 15


def _utcnow():
    return datetime.now(timezone.utc)


def _as_utc(dt: datetime | None) -> datetime | None:
    """Normalize SQLite datetimes to timezone-aware UTC for safe comparisons."""
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter(
            or_(
                User.username == form.username.data.strip(),
                User.email == form.email.data.strip().lower(),
            )
        ).first():
            flash("Registration could not be completed.", "error")
            log_event("REGISTER_FAIL", "Duplicate username or email", request=request)
            return render_template("register.html", form=form)
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower(),
            password_hash=hash_password(form.password.data),
        )
        db.session.add(user)
        db.session.commit()
        log_event("REGISTER_OK", f"User registered: {user.username}", user_id=user.id, request=request)
        flash("Account created. Please log in.", "success")
        return redirect(url_for("auth.login"))
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("20 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    form = LoginForm()
    auth_error = None
    if form.validate_on_submit():
        username = form.username.data.strip()
        user = User.query.filter_by(username=username).first()
        now = _utcnow()

        lock_until = _as_utc(user.locked_until) if user else None
        if user and lock_until and lock_until > now:
            flash("Account temporarily locked. Try again later.", "error")
            log_event("AUTH_LOCK", f"Locked user login attempt: {username}", user_id=user.id, request=request)
            return render_template("login.html", form=form)

        if user and check_password(form.password.data, user.password_hash):
            user.failed_login_count = 0
            user.locked_until = None
            db.session.commit()
            login_user(user, remember=False)
            from flask import session

            session.permanent = True
            log_event("AUTH_SUCCESS", "Login success", user_id=user.id, request=request)
            flash("Logged in successfully.", "success")
            return redirect(url_for("main.dashboard"))

        if user:
            user.failed_login_count = (user.failed_login_count or 0) + 1
            if user.failed_login_count >= MAX_FAILED:
                user.locked_until = now + timedelta(minutes=LOCK_MINUTES)
                log_event(
                    "AUTH_LOCK",
                    f"Account locked after failures: {username}",
                    user_id=user.id,
                    request=request,
                )
            db.session.commit()
            log_event("AUTH_FAIL", "Invalid password", user_id=user.id, request=request)
        else:
            log_event("AUTH_FAIL", "Invalid username", request=request)

        auth_error = "Invalid username or password."

    return render_template("login.html", form=form, auth_error=auth_error)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        uid = current_user.id
        uname = current_user.username
        logout_user()
        log_event("AUTH_LOGOUT", f"User logged out: {uname}", user_id=uid, request=request)
        flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
