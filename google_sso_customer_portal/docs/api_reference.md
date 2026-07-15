# API Reference

Base path: `/api/v1/auth`

## GET /login/google
Initiates the Google OAuth 2.0 flow (FR-1). Generates a signed `state` token, builds the
Google authorisation URL (scopes: `openid email profile`) and issues a `307` redirect.

## GET /callback/google
Handles the OAuth 2.0 callback (FR-2..FR-6).

Query params: `code`, `state`, optional `error`.

Flow:
1. Validate `state` (CSRF, NFR-1).
2. Exchange `code` for tokens at Google Token endpoint.
3. Fetch user profile from Google UserInfo endpoint.
4. Create/lookup `User` (FR-4/FR-5).
5. Issue signed JWT (FR-6) and redirect to dashboard.

Errors (FR-9, AC-4):
```json
{ "error": "authentication_error", "detail": "Failed to authenticate with Google" }
```
- `400` invalid/missing `code` or `state`
- `502` Google token/userinfo failure

## POST /logout
Requires `Authorization: Bearer <jwt>`. Adds the token `jti` to `TokenDenylist` (FR-8).

Response `200`:
```json
{ "detail": "Successfully logged out" }
```

## GET /me
Requires `Authorization: Bearer <jwt>`. Returns the authenticated user's profile.
