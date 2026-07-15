# Google Single Sign-On (SSO) for Customer Portal

SCRUM-5 — FastAPI service that authenticates Customer Portal users via Google OAuth 2.0 and issues stateless JWTs.

## Tech Stack
FastAPI + SQLAlchemy (async) + PostgreSQL + JWT. Outbound calls via httpx.

## Features
- `Sign in with Google` OAuth 2.0 authorization-code flow with CSRF `state`.
- Automatic user provisioning on first login; lookup by `google_id` on subsequent logins.
- Signed JWT issuance, JTI denylist logout, and structured auth audit logging.

## Quickstart
```bash
cd google_sso
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in Google credentials
uvicorn main:app --reload
```

## API
| Method | Path | Description |
|--------|------|-------------|
| GET | /api/v1/auth/login/google | Start OAuth flow (returns authorization URL + state) |
| GET | /api/v1/auth/callback/google | Handle callback, exchange code, return JWT |
| POST | /api/v1/auth/logout | Revoke current JWT (denylist JTI) |
| GET | /api/v1/auth/me | Current authenticated user |

## Tests
```bash
pytest
```

See `docs/` for setup, architecture, data model and API reference.
