# Google OAuth 2.0 Setup

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and create/select a project.
2. Configure the OAuth consent screen (External) with scopes `openid`, `email`, `profile`.
3. Create **OAuth client ID** credentials of type *Web application*.
4. Add an authorized redirect URI matching `GOOGLE_REDIRECT_URI`, e.g. `https://localhost:8000/api/v1/auth/callback/google`.
5. Copy the generated **Client ID** and **Client secret** into your `.env`:

```env
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GOOGLE_REDIRECT_URI=https://localhost:8000/api/v1/auth/callback/google
```

Secrets must only live in environment variables and never be committed.
