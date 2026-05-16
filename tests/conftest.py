"""Pytest fixtures: test app, client, env for crypto."""
from __future__ import annotations

import os

import pytest
from cryptography.fernet import Fernet


@pytest.fixture(scope="session", autouse=True)
def _test_env() -> None:
    os.environ.setdefault("ENCRYPTION_KEY", Fernet.generate_key().decode())
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
    os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture()
def app():
    from securedoc import create_app

    application = create_app(config_name="testing")
    yield application


@pytest.fixture()
def client(app):
    return app.test_client()
