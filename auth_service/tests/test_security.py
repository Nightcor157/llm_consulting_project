from app.core.security import create_access_token, decode_token, hash_password, verify_password


def test_hash_password_and_verify() -> None:
    plain_password = "password123"

    password_hash = hash_password(plain_password)

    assert password_hash != plain_password
    assert verify_password(plain_password, password_hash) is True
    assert verify_password("wrong-password", password_hash) is False


def test_create_and_decode_access_token() -> None:
    token = create_access_token(subject=42, role="user")

    payload = decode_token(token)

    assert payload["sub"] == "42"
    assert payload["role"] == "user"
    assert "iat" in payload
    assert "exp" in payload
