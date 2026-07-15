"""Custom exceptions and structured error handling (FR-9)."""
from fastapi import Request
from fastapi.responses import JSONResponse


class AuthError(Exception):
    def __init__(self, detail: str, status_code: int = 400, error: str = "authentication_error") -> None:
        self.detail = detail
        self.status_code = status_code
        self.error = error
        super().__init__(detail)


async def auth_error_handler(request: Request, exc: AuthError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error, "detail": exc.detail},
    )
