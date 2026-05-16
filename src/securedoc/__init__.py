"""
SecureDoc — secure document sharing prototype (SSD Assignment 3).

Package exposes :func:`create_app` for Flask application factory pattern.
"""
from __future__ import annotations

from securedoc.app_factory import create_app

__all__ = ["create_app"]
