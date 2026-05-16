"""
Flask application factory.

Wires extensions, blueprints, Talisman, CSRF, and instance paths.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask
from flask_talisman import Talisman
from flask_wtf.csrf import generate_csrf

from securedoc.config.settings import CONFIG_MAP
from securedoc.extensions import csrf, db, limiter, login_manager
from securedoc.models.user import User


def create_app(config_name: str | None = None) -> Flask:
    load_dotenv()
    cfg_name = config_name or os.getenv("FLASK_ENV", "development")
    config_class = CONFIG_MAP.get(cfg_name, CONFIG_MAP["development"])

    root = Path(__file__).resolve().parent.parent.parent
    instance_path = root / "instance"
    instance_path.mkdir(parents=True, exist_ok=True)

    app = Flask(
        __name__,
        instance_path=str(instance_path),
        template_folder=str(Path(__file__).parent / "templates"),
        static_folder=str(Path(__file__).parent / "static"),
    )
    app.config.from_object(config_class)

    if app.config["SQLALCHEMY_DATABASE_URI"].startswith("sqlite:///"):
        uri = app.config["SQLALCHEMY_DATABASE_URI"]
        if uri == "sqlite:///securedoc.db":
            app.config["SQLALCHEMY_DATABASE_URI"] = (
                "sqlite:///" + str(instance_path / "securedoc.db")
            )

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"

    @app.context_processor
    def _csrf():
        return dict(csrf_token=generate_csrf)

    @login_manager.user_loader
    def load_user(user_id: str):
        return db.session.get(User, int(user_id))

    storage = instance_path / app.config["STORAGE_SUBDIR"]
    storage.mkdir(parents=True, exist_ok=True)
    app.config["STORAGE_PATH"] = str(storage)

    # Talisman defaults session_cookie_secure=True, which drops the session cookie on plain
    # HTTP (e.g. http://192.168.x.x:5000). No session => CSRF fails on POST (register/login).
    if os.getenv("FLASK_ENV") == "production":
        Talisman(app, force_https=True, content_security_policy=None)
    else:
        Talisman(
            app,
            force_https=False,
            content_security_policy=None,
            session_cookie_secure=False,
        )

    from securedoc.routes.auth import auth_bp
    from securedoc.routes.documents import documents_bp
    from securedoc.routes.main import main_bp
    from securedoc.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(documents_bp, url_prefix="/documents")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    with app.app_context():
        import securedoc.models  # noqa: F401 — register metadata before create_all
        db.create_all()

    return app
