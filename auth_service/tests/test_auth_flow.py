import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_login_me_flow(client: AsyncClient) -> None:
    register_response = await client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "password123"},
    )
    assert register_response.status_code == 201
    registered_user = register_response.json()
    assert registered_user["email"] == "surname@email.com"
    assert "password_hash" not in registered_user

    login_response = await client.post(
        "/auth/login",
        data={"username": "surname@email.com", "password": "password123"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == "surname@email.com"


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    payload = {"email": "surname@email.com", "password": "password123"}

    first_response = await client.post("/auth/register", json=payload)
    second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.asyncio
async def test_login_with_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post(
        "/auth/register",
        json={"email": "surname@email.com", "password": "password123"},
    )

    response = await client.post(
        "/auth/login",
        data={"username": "surname@email.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_without_token_returns_401(client: AsyncClient) -> None:
    response = await client.get("/auth/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token_returns_401(client: AsyncClient) -> None:
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer not-a-jwt"},
    )

    assert response.status_code == 401
