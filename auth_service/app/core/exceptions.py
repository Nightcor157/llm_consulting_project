from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class BaseHTTPException(HTTPException):
    status_code: int = 500
    detail: str = "Internal server error"
    headers: dict[str, str] | None = None

    def __init__(self, detail: str | None = None) -> None:
        super().__init__(
            status_code=self.status_code,
            detail=detail if detail is not None else self.detail,
            headers=self.headers,
        )


class UserAlreadyExistsError(BaseHTTPException):
    status_code = 409
    detail = "User with this email already exists"


class InvalidCredentialsError(BaseHTTPException):
    status_code = 401
    detail = "Invalid email or password"
    headers = {"WWW-Authenticate": "Bearer"}


class InvalidTokenError(BaseHTTPException):
    status_code = 401
    detail = "Invalid token"
    headers = {"WWW-Authenticate": "Bearer"}


class TokenExpiredError(BaseHTTPException):
    status_code = 401
    detail = "Token expired"
    headers = {"WWW-Authenticate": "Bearer"}


class UserNotFoundError(BaseHTTPException):
    status_code = 404
    detail = "User not found"


class PermissionDeniedError(BaseHTTPException):
    status_code = 403
    detail = "Permission denied"


async def base_http_exception_handler(
    request: Request,
    exc: BaseHTTPException,
) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
