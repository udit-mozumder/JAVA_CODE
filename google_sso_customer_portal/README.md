# Customer Portal - Google Single Sign-On (SSO)

Implementation of **SCRUM-5: Implement Google Single Sign-On (SSO) for Customer Portal**.

Tech stack: **FastAPI + SQLAlchemy (async) + PostgreSQL + JWT**.

## Business Objective
Simplify user authentication in the Customer Portal by integrating Google OAuth 2.0 SSO,
eliminating the need for separate credentials, improving user experience, and reducing
account management overhead.

## Features
- Google OAuth 2.0 authorization-code flow with CSRF `state` protection (NFR-1)
- Automatic user provisioning on first login (FR-4) and lookup on subsequent logins (FR-5)
- Signed JWT session tokens with configurable expiry (FR-6, NFR-3)
- Auth audit logging of every success/failure/logout event (FR-7, NFR-5)
- Stateless logout via JWT JTI denylist (FR-8)
- Structured JSON logging (NFR-9) and Pydantic Settings configuration (NFR-8)

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/auth/login/google` | Initiate Google OAuth 2.0 flow |
| GET | `/api/v1/auth/callback/google` | Handle OAuth callback, issue JWT |
| POST | `/api/v1/auth/logout` | Revoke session (denylist JTI) |
| GET | `/api/v1/auth/me` | Return authenticated user profile |

## Getting Started
```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env   # fill in Google + DB credentials
alembic upgrade head
uvicorn main:app --reload
```

## Running Tests
```bash
pytest -q
```

## Project Structure
```
app/
  api/v1/endpoints/auth.py     # HTTP endpoints
  core/config.py               # Pydantic settings
  core/security.py             # JWT + CSRF state helpers
  db/                          # engine, session, ORM models
  schemas/                     # Pydantic request/response models
  services/                    # google_oauth, user, auth orchestration
  middleware/auth_middleware.py
  utils/                       # logger, errors
tests/                         # unit + integration tests
alembic/                       # migrations
docs/                          # architecture + api reference
```

## Documentation
- [API Reference](docs/api_reference.md)
- [Architecture](docs/architecture.md)
