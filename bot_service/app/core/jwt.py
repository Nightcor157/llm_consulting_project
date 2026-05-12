from typing import Any

from jose import ExpiredSignatureError, JWTError, jwt

from app.core.config import settings


class TokenValidationError(ValueError):
    pass


class TokenExpiredValidationError(TokenValidationError):
    pass


def decode_and_validate(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_alg])
    except ExpiredSignatureError as exc:
        raise TokenExpiredValidationError("Token expired") from exc
    except JWTError as exc:
        raise TokenValidationError("Invalid token") from exc

    if not payload.get("sub"):
        raise TokenValidationError("Token does not contain sub")
    return payload
