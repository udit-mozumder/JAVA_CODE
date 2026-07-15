# Architecture

## Overview
The service implements Google OAuth 2.0 SSO for the Customer Portal using a layered
FastAPI application. Sessions are stateless JWTs to support horizontal scaling (NFR-6).

## Layers
- API layer (`app/api/v1/endpoints/auth.py`): HTTP routing.
- Service layer (`app/services/`): GoogleOAuthService, UserService, AuthService.
- Data layer (`app/db/`): async SQLAlchemy engine/session + ORM models.
- Core (`app/core/`): Pydantic settings and security (JWT/CSRF).
- Cross-cutting (`app/middleware`, `app/utils`): auth context, logging, errors.

## OAuth 2.0 Sequence
```
Client -> GET /login/google -> 307 -> Google consent
Google -> GET /callback/google?code&state
  -> verify state (CSRF)
  -> POST Google token endpoint (code -> tokens)
  -> GET Google userinfo (access_token -> profile)
  -> upsert User, issue JWT
  -> 307 redirect to dashboard (JWT)
```

## Data Model
- users: id (UUID PK), google_id (unique), email (unique), display_name, avatar_url,
  is_active, created_at, last_login_at.
- auth_audit_logs: id, user_id (FK, nullable), event_type, ip_address, user_agent,
  error_message, created_at.
- token_denylist: id, jti (unique), user_id (FK), revoked_at, expires_at.

## Security
- CSRF protection via signed `state` (itsdangerous), NFR-1.
- HTTPS-only, secure cookies, NFR-2.
- Secrets from environment via Pydantic Settings, NFR-4/NFR-8.
- JWT expiry configurable (60 min access / 7 day refresh), NFR-3.
