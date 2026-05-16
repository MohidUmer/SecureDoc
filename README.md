# SecureDoc – Encrypted Document Sharing Platform
<!-- Achievement: Secure Software Development Excellence -->

## 1. Project Overview

### 1.1 Why
SecureDoc was built to demonstrate **secure software development principles** in a real-world document management application.
It addresses the critical need for security-first design — tackling common vulnerabilities such as CSRF attacks, SQL injection, brute-force login attempts, insecure file uploads, weak session management, and insufficient access control — while delivering a polished, modern user experience for secure document collaboration.

### 1.2 What
A Flask-based secure document sharing application that provides:

- **User Authentication** with bcrypt-hashed passwords and account lockout
- **Role-Based Access Control (RBAC)** with granular sharing permissions
- **CSRF-Protected Forms** via Flask-WTF
- **Rate-Limited Endpoints** to prevent brute-force attacks
- **Secure File Uploads** with type validation and size limits
- **Document Encryption at Rest** using Fernet (AES + HMAC)
- **Security Headers** enforced via Flask-Talisman
- **Audit Logging** for security-relevant events
- **Document Versioning** with encrypted version history
- **Comment System** with XSS protection

### 1.3 How (High-Level)
- Users register and authenticate through a secure login system with rate limiting
- Documents are uploaded, encrypted, and stored with metadata in the database
- File attachments are validated, sanitized, and encrypted before storage
- Users can share documents with others using role-based permissions (View, Comment, Edit)
- Rate limiting, CSRF tokens, and security headers protect every endpoint
- Sensitive configuration is loaded from environment variables
- All security-relevant events are logged for audit trails

---

## 2. Features

| Icon | Feature | Description |
|------|---------|-------------|
| 🔐 | **Bcrypt Password Hashing** | Passwords are never stored in plaintext |
| 🛡️ | **CSRF Protection** | All forms protected via Flask-WTF CSRF tokens |
| 🚦 | **Rate Limiting** | Login endpoint restricted to 20 attempts/minute, register to 5/hour |
| 📎 | **Secure File Uploads** | Type whitelist, filename sanitization, 25 MB limit |
| 🏷️ | **Role-Based Access (RBAC)** | Owner-based operations with granular sharing roles |
| 🔒 | **Security Headers** | Talisman enforces X-Frame-Options, HSTS, etc. |
| 🍪 | **Secure Cookies** | HTTPOnly, SameSite=Lax, Secure flags enabled |
| 🔐 | **Document Encryption** | Fernet (AES + HMAC) encryption for files at rest |
| 📋 | **Audit Logging** | Comprehensive security event logging for admin review |
| 📝 | **Document Versioning** | Encrypted version history with parent-child tracking |
| 💬 | **Comment System** | Secure commenting with XSS protection |
| 🔒 | **Account Lockout** | Automatic lockout after 5 failed login attempts |
| 🎨 | **Modern UI** | Clean, responsive interface with Bootstrap 5 |

---

## 3. Tech Stack

**Backend:**

- Python 3.8+
- Flask 3.x
- Flask-SQLAlchemy (ORM)
- Flask-Login (Session Management)
- Flask-Bcrypt (Password Hashing)
- Flask-WTF (CSRF Protection)
- Flask-Talisman (Security Headers)
- Flask-Limiter (Rate Limiting)
- python-dotenv (Environment Management)
- cryptography (Fernet Encryption)

**Frontend:**

- HTML5 / CSS3
- Bootstrap 5.3
- Jinja2 Templates

**Database:**

- SQLite (development)

**Testing:**

- pytest 8.x

---

## 4. Project Structure

```
SecureDoc/
├── src/
│   └── securedoc/
│       ├── __init__.py              # Package initialization
│       ├── app_factory.py           # Flask application factory
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py          # Configuration classes
│       ├── extensions.py            # Flask extensions
│       ├── forms.py                 # WTForms definitions
│       ├── middleware/              # Request hooks
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py              # User model
│       │   ├── document.py          # Document & version models
│       │   ├── share.py             # Share/ACL model
│       │   ├── comment.py           # Comment model
│       │   └── audit_log.py         # Audit log model
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth.py              # Authentication routes
│       │   ├── documents.py         # Document CRUD routes
│       │   ├── main.py              # Main & dashboard routes
│       │   └── admin.py             # Admin audit log routes
│       ├── services/
│       │   ├── __init__.py
│       │   ├── crypto_service.py    # Encryption/decryption
│       │   ├── authorization.py     # RBAC authorization
│       │   ├── audit_service.py     # Audit logging
│       │   └── validation_service.py # Input validation
│       ├── utils/
│       │   ├── __init__.py
│       │   └── passwords.py          # Password hashing utilities
│       ├── static/                  # CSS, JS, images
│       └── templates/               # HTML templates
├── tests/
│   ├── conftest.py                  # Pytest fixtures
│   ├── test_auth.py                 # Authentication tests
│   └── test_authz.py                # Authorization tests
├── docs/
│   ├── security-decisions.md        # Security design decisions
│   └── screenshots/                 # Application screenshots
├── instance/                        # SQLite database (gitignored)
├── run.py                           # Application entry point
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── .gitignore                       # Git exclusion rules
└── README.md                        # This file
```

---

## 5. Setup & Usage

### 5.1 Prerequisites

- Python 3.8 or later
- pip package manager

### 5.2 Installation

```bash
git clone https://github.com/your-username/SecureDoc.git
cd SecureDoc
pip install -r requirements.txt
```

### 5.3 Environment Configuration

Copy `.env.example` to `.env` and fill in the values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
FLASK_ENV=development
SECRET_KEY=change-me-to-long-random-hex
SESSION_TIMEOUT_MINUTES=30
DATABASE_URI=sqlite:///securedoc.db
ENCRYPTION_KEY=your-fernet-key-here
```

**Generate an encryption key:**

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### 5.4 Initialize Database

The database is automatically created on first run. No manual initialization needed.

### 5.5 Run Locally

```bash
python run.py
```

Access the application at: **http://localhost:5000**

### 5.6 Run Tests

```bash
pytest
```

---

## 6. Major Components

### 6.1 Authentication System
- Registration with input validation (regex, length, email format)
- Bcrypt password hashing with salt (12 rounds)
- Session-based authentication with Flask-Login
- Login rate limiting (20 attempts/minute)
- Account lockout after 5 failed attempts (15-minute lock)
- Generic error messages to prevent user enumeration

### 6.2 Document Management (CRUD)
- Upload documents with optional file attachments
- View document details with metadata and version history
- Download documents with on-the-fly decryption
- Update documents with new versions
- Delete documents with cascading cleanup

### 6.3 Secure File Upload Engine
- Whitelist validation: `pdf, txt, png, jpg, jpeg, doc, docx`
- Filename sanitization to prevent path traversal
- 25 MB maximum file size enforcement
- Fernet encryption (AES + HMAC) for files at rest
- Unique stored filenames (token_urlsafe) to prevent collisions
- SHA-256 integrity hashing for content verification

### 6.4 Role-Based Access Control
- Central authorization service (`services/authorization.py`)
- Owner has full control (VIEW, DOWNLOAD, COMMENT, EDIT, SHARE, DELETE)
- Grantees receive role-based permissions:
  - **VIEW**: View and download only
  - **COMMENT**: View, download, and comment
  - **EDIT**: View, download, comment, and create new versions
- Server-side authorization on every document operation
- IDOR prevention through mandatory authorization checks

### 6.5 Document Versioning
- Encrypted version history with parent-child tracking
- Each version stored as separate ciphertext file
- Version metadata includes creator, timestamp, and size
- Automatic version numbering
- Cascading cleanup on document deletion

### 6.6 Audit Logging
- Comprehensive security event logging
- Events: AUTH_SUCCESS, AUTH_FAIL, AUTH_LOCK, REGISTER_OK, DOCUMENT_UPLOAD, DOCUMENT_DOWNLOAD, DOCUMENT_DELETE, SHARE_CHANGED, COMMENT_ADD, DECRYPT_FAIL
- Logs include event type, message, user_id, IP address, and extra context
- Admin-only audit log viewer at `/admin/audit`
- No sensitive data (passwords, file contents) logged

---

## 7. Security Implementation Details

| Security Layer | Implementation | Threat Mitigated |
|----------------|----------------|------------------|
| Password Storage | Bcrypt hashing with salt (12 rounds) | Credential theft |
| CSRF Protection | Flask-WTF hidden tokens on all forms | Cross-Site Request Forgery |
| Rate Limiting | Flask-Limiter (20/min login, 5/hour register) | Brute-force attacks |
| Security Headers | Flask-Talisman (X-Frame, HSTS, etc.) | Clickjacking, MITM |
| Input Validation | WTForms validators + regex + custom validation | Injection attacks |
| File Upload | Whitelist + sanitization + size limit + encryption | Malicious file upload |
| Session Security | HTTPOnly, SameSite=Lax, Secure (production) | Session hijacking |
| Document Encryption | Fernet (AES + HMAC) at rest | Data breach exposure |
| Authorization | Central RBAC service on every operation | IDOR, unauthorized access |
| Account Lockout | 5 failures → 15-minute lock | Brute-force credential attacks |
| Audit Logging | Database-backed event logging | Incident investigation |
| Environment Secrets | python-dotenv for keys and URIs | Secret exposure in code |

---

## 8. System Workflow

```
User Registers → Password Hashed (Bcrypt) → Account Created
       ↓
User Logs In → Rate Limit Check → Account Lockout Check → Session Established
       ↓
User Uploads Document → CSRF Validated → File Validated → Encrypted (Fernet) → Stored
       ↓
User Shares Document → Grantee Assigned Role → ACL Entry Created
       ↓
User Downloads Document → Authorization Check → Decrypted (Fernet) → Served
       ↓
User Creates Version → Authorization Check → New Encrypted File → Version Record
       ↓
User Comments → Authorization Check → XSS-Safe Storage → Logged
       ↓
User Deletes Document → Authorization Check → Cascading Cleanup → Audit Logged
       ↓
Admin Reviews Audit → Admin Check → Event List Displayed
```

---

## 9. Data Handling & Privacy

- Passwords are **hashed and salted** with bcrypt — never stored in plaintext
- User sessions are **HTTPOnly** and **SameSite** protected
- Document files are **encrypted at rest** using Fernet (AES + HMAC)
- File uploads are **sanitized** and stored with collision-resistant names
- Audit logs **exclude sensitive data** (no passwords, file contents, tokens)
- Environment variables keep secrets out of source code
- No external analytics or tracking is implemented

---

## 10. API & Stability

- Rate limiting enforced via Flask-Limiter (200/day, 100/hour global; 20/min login, 5/hour register)
- Custom error handlers for 403, 404 responses
- Debug mode disabled in production
- Database auto-creation on first run
- Comprehensive test coverage for auth and authz

---

## 11. Limitations

- Single SQLite database (not suitable for production at scale)
- No real-time collaboration features
- No password reset / email verification flow
- No document search within file contents
- No file preview functionality
- Web-only interface (no mobile app)
- Encryption key rotation not implemented
- No backup/restore functionality

---

## 12. Usage Example

```
1. Register a new account → Login
2. Upload a document with title and file → File encrypted and stored
3. View document details → See metadata, versions, comments
4. Share document with another user → Assign role (View/Comment/Edit)
5. Grantee accesses shared document → Permissions enforced
6. Add comments to document → Collaborate with team
7. Create new version → Upload updated file → Version history tracked
8. Download document → Decrypted on-the-fly
9. Delete document → Cascading cleanup of versions, shares, comments
10. Admin reviews audit log → Monitor security events
```

---

## 13. Future Improvements

- End-to-end encryption with per-user keys
- Document search within file contents
- File preview functionality (PDF, images)
- Password reset via email verification
- Two-factor authentication (2FA)
- Database migration to PostgreSQL for production
- Docker containerization
- Key rotation mechanism
- Backup and restore functionality
- Real-time collaboration via WebSockets
- Mobile application (React Native / Flutter)
- Advanced audit log filtering and export
- Document expiration and auto-deletion

---

## 14. Educational & Practical Value

SecureDoc demonstrates:

- **Secure authentication** with password hashing, rate limiting, and account lockout
- **CSRF protection** across all state-changing operations
- **Rate limiting** to prevent abuse and brute-force attacks
- **Secure file handling** with validation, sanitization, and encryption
- **Role-based access control** with centralized authorization
- **Document encryption at rest** using industry-standard Fernet
- **Security headers** via middleware
- **Environment-based configuration** for secret management
- **Audit logging** for security event traceability
- **Document versioning** with encrypted history
- **Modern software architecture** with clean separation of concerns

---

## 15. Author & Contact

**Team:** Mohid Umer  
**Project:** Secure Software Development

---

## 16. License & Usage

- Educational and personal use only
- Proper attribution required
- Not permitted for academic plagiarism
- See repository LICENSE for details

---

> **SecureDoc** showcases modern secure software development principles through a practical, well-designed document sharing application that prioritizes security at every layer of the stack, from authentication to encryption at rest.
