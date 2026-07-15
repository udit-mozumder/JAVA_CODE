"""Application entrypoint for the Customer Portal Google SSO service (SCRUM-5)."""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.endpoints import auth as auth_endpoints
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.middleware.auth_middleware import AuthContextMiddleware
from app.utils.errors import AuthError, auth_error_handler
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup (use Alembic in production)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("application_startup", extra={"extra_fields": {"app": settings.PROJECT_NAME}})
    yield
    await engine.dispose()
    logger.info("application_shutdown")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )
    app.add_middleware(AuthContextMiddleware)
    app.add_exception_handler(AuthError, auth_error_handler)
    app.include_router(
        auth_endpoints.router,
        prefix=f"{settings.API_V1_PREFIX}/auth",
        tags=["auth"],
    )

    @app.get("/health", tags=["health"])
    async def health() -> dict:
        return {"status": "ok"}

    return app


app = create_app()
