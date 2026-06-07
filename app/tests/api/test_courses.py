import pytest
from httpx import AsyncClient

from app.tests.conftest import (
    create_user_and_token,
    create_test_course,
    auth_headers,
)


# ── GET /courses/

@pytest.mark.asyncio
async def test_list_active_courses(client: AsyncClient):
    # Create admin and two courses
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    await create_test_course(client, admin_token, title="Python 101", code="PY101")
    await create_test_course(client, admin_token, title="Java 101", code="JV101")

    response = await client.get("/api/v1/courses/")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 2


@pytest.mark.asyncio
async def test_list_courses_excludes_inactive(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="ACT01")
    await create_test_course(client, admin_token, code="INACT01")

    # Deactivate the second course
    await client.patch(
        f"/api/v1/courses/{course['id'] + 1}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )

    response = await client.get("/api/v1/courses/")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 1


# ── GET /courses/{id}

@pytest.mark.asyncio
async def test_get_course_by_id(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="GET01")

    response = await client.get(f"/api/v1/courses/{course['id']}")
    assert response.status_code == 200
    assert response.json()["code"] == "GET01"


@pytest.mark.asyncio
async def test_get_course_not_found(client: AsyncClient):
    response = await client.get("/api/v1/courses/999")
    assert response.status_code == 404


# ── POST /courses/ 

@pytest.mark.asyncio
async def test_create_course_admin(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    response = await client.post(
        "/api/v1/courses/",
        json={"title": "New Course", "code": "NEW01", "capacity": 25},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code"] == "NEW01"
    assert data["capacity"] == 25
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_create_course_student_forbidden(client: AsyncClient):
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    response = await client.post(
        "/api/v1/courses/",
        json={"title": "Forbidden", "code": "FB01", "capacity": 10},
        headers=auth_headers(student_token),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_course_duplicate_code(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    await create_test_course(client, admin_token, code="DUP01")
    response = await client.post(
        "/api/v1/courses/",
        json={"title": "Duplicate", "code": "DUP01", "capacity": 10},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_create_course_invalid_capacity(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    response = await client.post(
        "/api/v1/courses/",
        json={"title": "Bad Cap", "code": "BAD01", "capacity": 0},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 422


# ── PUT /courses/{id} 

@pytest.mark.asyncio
async def test_update_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="UPD01")

    response = await client.put(
        f"/api/v1/courses/{course['id']}",
        json={"title": "Updated", "code": "UPD01", "capacity": 50, "is_active": True},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated"
    assert response.json()["capacity"] == 50


# ── PATCH /courses/{id} 

@pytest.mark.asyncio
async def test_patch_deactivate_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="PAT01")

    response = await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is False


@pytest.mark.asyncio
async def test_patch_activate_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="PAT02")

    # Deactivate first
    await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )
    # Re-activate
    response = await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"is_active": True},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert response.json()["is_active"] is True


# ── DELETE /courses/{id}

@pytest.mark.asyncio
async def test_delete_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="DEL01")

    response = await client.delete(
        f"/api/v1/courses/{course['id']}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_delete_course_not_found(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    response = await client.delete(
        "/api/v1/courses/999",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 404
