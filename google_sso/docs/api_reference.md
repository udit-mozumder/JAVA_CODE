# API Reference

Base path: `/api/v1/auth`

## GET /login/google
Initiates the Google OAuth 2.0 flow.

**200 Response**
```json
{ "authorization_url": "https://accounts.google.com/o/oauth2/v2/auth?...", "state": "<random>" }
```

## GET /callback/google
Query params: `code`, `state`, optional `error`.

**200 Response**
```json
{ "access_token": "<jwt>", "token_type": "bearer", "expires_in": 3600 }
```
Errors: `400` invalid state / missing code / google error, `502` token exchange failure.

## POST /logout
Auth: `Authorization: Bearer <jwt>`.

**200 Response**
```json
{ "detail": "Successfully logged out" }
```

## GET /me
Auth: `Authorization: Bearer <jwt>`. Returns the authenticated user profile.
