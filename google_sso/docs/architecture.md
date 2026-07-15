# Architecture

```
Client (SPA)
   |  GET /login/google
   v
FastAPI auth endpoints  --->  GoogleOAuthService  --->  Google OAuth 2.0
   |                                |
   |                                v
   |                          AuthService
   |             /            |            \
   v            v             v             v
 UserRepository  AuthAuditRepository  TokenDenylistRepository
   \_________________ PostgreSQL (async SQLAlchemy) _________________/
```

## Layers
- **Endpoints** (`app/api/v1/endpoints`): HTTP concerns, validation, error mapping.
- **Services** (`app/services`): OAuth orchestration and JWT lifecycle.
- **Repositories** (`app/db/repositories`): all database access.
- **Core** (`app/core`): configuration and JWT security primitives.
- **Middleware** (`app/middleware`): Bearer-token authentication dependency.

JWTs are stateless; only a denylist check hits the DB on protected routes.
