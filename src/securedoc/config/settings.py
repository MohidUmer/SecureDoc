"""
Application configuration.

Security-related settings are loaded from environment variables only
(no hardcoded secrets). See .env.example.
"""
from __future__ import annotations

import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URI",
        "sqlite:///securedoc.db",
    )
    PERMANENT_SESSION_LIFETIME = timedelta(
        minutes=int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
    )
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    WTF_CSRF_TIME_LIMIT = None
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_UPLOAD_MB", "25")) * 1024 * 1024
    ALLOWED_UPLOAD_EXTENSIONS = frozenset(
        os.getenv(
            "ALLOWED_EXTENSIONS",
            "pdf,txt,png,jpg,jpeg,doc,docx",
        ).split(",")
    )
    STORAGE_SUBDIR = "ciphertext"


class DevelopmentConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
