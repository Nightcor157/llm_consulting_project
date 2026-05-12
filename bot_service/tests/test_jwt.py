from datetime import datetime, timedelta, timezone

import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import TokenValidationError, decode_and_validate


def make_token(subject: str = "42", role: str = "user") -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": subject,
            "role": role,
            "iat": int(now.timestamp()),
            "exp": now + timedelta(minutes=5),
        },
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )


def test_decode_and_validate_valid_token() -> None:
    token = make_token(subject="42")

    payload = decode_and_validate(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "user"


def test_decode_and_validate_invalid_token() -> None:
    with pytest.raises(TokenValidationError):
        decode_and_validate("not-a-jwt")
