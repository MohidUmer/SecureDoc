"""
User model — authentication identity.

Security: passwords stored as bcrypt hashes only; never log plaintext passwords.
"""
from __future__ import annotations

from flask_login import UserMixin

from securedoc.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    failed_login_count = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime, nullable=True)

    documents = db.relationship(
        "Document",
        backref="owner",
        lazy="dynamic",
        foreign_keys="Document.owner_id",
    )

    def __repr__(self) -> str:
        return f"<User {self.username}>"
