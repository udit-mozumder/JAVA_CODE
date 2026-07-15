"""Application configuration loaded from environment variables."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    APP_NAME: str = 'Google SSO for Customer Portal'
    APP_VERSION: str = '1.0.0'
    API_V1_PREFIX: str = '/api/v1'

    GOOGLE_CLIENT_ID: str = ''
    GOOGLE_CLIENT_SECRET: str = ''
    GOOGLE_REDIRECT_URI: str = 'http://localhost:8000/api/v1/auth/callback/google'

    GOOGLE_AUTH_URI: str = 'https://accounts.google.com/o/oauth2/v2/auth'
    GOOGLE_TOKEN_URI: str = 'https://oauth2.googleapis.com/token'
    GOOGLE_USERINFO_URI: str = 'https://www.googleapis.com/oauth2/v2/userinfo'
    GOOGLE_SCOPES: str = 'openid email profile'

    JWT_SECRET_KEY: str = 'change-me'
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    DATABASE_URL: str = 'sqlite+aiosqlite:///./app.db'
    REDIS_URL: str = ''


settings = Settings()
