import pytest
from httpx import AsyncClient

from app.tests.conftest import create_user, get_token, create_user_and_token, auth_headers


# ── POST /auth/register 

@pytest.mark.asyncio
async def test_register_student(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "secret123",
            "role": "student",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "alice@example.com"
    assert data["role"] == "student"
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_admin(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "secret123",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    await create_user(client, email="dup@example.com")
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Dup",
            "email": "dup@example.com",
            "password": "secret123",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_register_invalid_role(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "name": "Bad",
            "email": "bad@example.com",
            "password": "secret123",
            "role": "superuser",
        },
    )
    assert response.status_code == 400
    assert "invalid role" in response.json()["detail"].lower()


# ── POST /auth/token 

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await create_user(client, email="login@example.com", password="mypassword")
    response = await client.post(
        "/api/v1/auth/token",
        data={"email": "login@example.com", "password": "mypassword"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await create_user(client, email="wrong@example.com", password="correct")
    response = await client.post(
        "/api/v1/auth/token",
        data={"email": "wrong@example.com", "password": "incorrect"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/token",
        data={"email": "ghost@example.com", "password": "any"},
    )
    assert response.status_code == 401


# ── GET /auth/me

@pytest.mark.asyncio
async def test_get_profile(client: AsyncClient):
    _, token = await create_user_and_token(client, email="me@example.com")
    response = await client.get("/api/v1/auth/me", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_get_profile_no_token(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
