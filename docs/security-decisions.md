# Security decisions (SecureDoc)

This document ties implementation choices to the SSD Assignment 2 threat model and common categories (e.g. OWASP-style). It is meant for reviewers and assessors.

## Authentication (A01 broken access control — identity)

- **Password storage:** Passwords are hashed with **bcrypt** (`securedoc.utils.passwords`). Plaintext passwords are never persisted or written to the audit log.
- **Sessions:** Flask-Login with **server-side session** (`SECRET_KEY`), **HTTP-only** cookies, **SameSite=Lax**, and **Secure** in production (`SESSION_COOKIE_SECURE` when `FLASK_ENV=production`).
- **Brute force:** Flask-Limiter on register/login routes; **account lockout** after repeated failed logins (`auth.py`) with a time-bounded `locked_until` field.
- **Logout:** POST-only logout with CSRF token to reduce CSRF-driven session termination tricks.

## Authorization (A01 — IDOR / horizontal privilege)

- **Central checks:** Every document action goes through `securedoc.services.authorization` (`authorize` / `authorize_by_id`). Routes do not trust client-supplied ids without these checks.
- **Ownership vs share:** Document **owner** has full control. **Grantees** receive a **role** (`VIEW`, `COMMENT`, `EDIT`) stored as a string in SQLite for portability.
- **Sensitive actions:** Only the **owner** may **share** or **delete** a document; grantees cannot escalate via shared links (enforced in `authorize`).

## Cryptography (A02 cryptographic failures)

- **At-rest files:** Uploads are encrypted with **Fernet** (AES + HMAC) using `ENCRYPTION_KEY` from the environment only — not stored next to ciphertext in the database.
- **Key management:** Operators must generate and protect `ENCRYPTION_KEY`; loss of the key implies loss of documents. Rotation is out of scope for this assignment prototype.
- **Integrity:** Fernet provides authenticated encryption; tampered blobs fail decryption and are logged (`DECRYPT_FAIL`).

## Injection and validation (A03 injection)

- **SQL:** SQLAlchemy ORM with bound parameters; no raw string SQL for user input.
- **XSS:** Jinja2 auto-escaping in templates; user comments rendered with `| e` where appropriate.
- **Uploads:** Extension allowlist, size limit (`MAX_CONTENT_LENGTH`), sanitized display names; content is treated as opaque bytes once validated.

## Design / misconfiguration (A04, A05)

- **CSRF:** Flask-WTF CSRF on state-changing forms; manual `csrf_token` on small multipart POSTs (new version, delete) that are not WTForms.
- **Headers:** Flask-Talisman enables baseline security headers; CSP is left flexible for this lab app (`content_security_policy=None`).
- **Secrets:** `.env` is gitignored; `.env.example` documents variables without real secrets.

## Logging and monitoring (A09)

- **Audit log:** Security-relevant events (auth success/fail, lockout, upload, download, share changes, decrypt failures, deletes) are appended to `audit_logs` with type, message, optional `user_id`, IP, and small `extra` field — **no** file contents or passwords.
- **Admin UI:** `/admin/audit` lists recent events for `is_admin` users only.

## Data integrity (A08)

- **Versioning:** New versions create new ciphertext files and version rows; old blobs can be removed or retained per policy (current code deletes files on document delete).
- **Comments:** Stored as text with length limits and validation in `validation_service`.

## Traceability to Assignment 2

Use cases from the design (upload, download, share with role, comment, version, search, audit) are implemented with the controls above so that **authentication**, **authorization**, **encryption at rest**, **CSRF**, and **auditability** are visible in code and configuration rather than only in diagrams.
