"""Authentication endpoint tests."""

from httpx import AsyncClient


async def test_register_creates_a_member(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "new@test.dev",
            "password": "password123",
            "full_name": "New Member",
        },
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["email"] == "new@test.dev"
    assert body["role"] == "member"
    assert "hashed_password" not in body


async def test_register_rejects_duplicate_email(client: AsyncClient) -> None:
    payload = {
        "email": "duplicate@test.dev",
        "password": "password123",
        "full_name": "Duplicate",
    }
    assert (await client.post("/api/v1/auth/register", json=payload)).status_code == 201

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 409
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json()["code"] == "duplicate_email"


async def test_login_and_read_profile(client: AsyncClient) -> None:
    payload = {
        "email": "login@test.dev",
        "password": "password123",
        "full_name": "Login Member",
    }
    await client.post("/api/v1/auth/register", json=payload)

    response = await client.post(
        "/api/v1/auth/login",
        data={"username": payload["email"], "password": payload["password"]},
    )
    assert response.status_code == 200, response.text
    token = response.json()["access_token"]

    profile = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    assert profile.json()["email"] == payload["email"]


async def test_login_with_wrong_password(client: AsyncClient) -> None:
    response = await client.post(
        "/api/v1/auth/login",
        data={"username": "missing@test.dev", "password": "nope"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


async def test_protected_endpoint_requires_token(client: AsyncClient) -> None:
    response = await client.get("/api/v1/loans")
    assert response.status_code == 401


async def test_health_check(client: AsyncClient) -> None:
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
