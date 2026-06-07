import pytest
from httpx import AsyncClient

from app.tests.conftest import (
    create_user_and_token,
    create_test_course,
    auth_headers,
)


# ── POST /enrollments/

@pytest.mark.asyncio
async def test_enroll_student(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="ENR01", capacity=30)

    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["course_id"] == course["id"]


@pytest.mark.asyncio
async def test_enroll_duplicate(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="DUP01", capacity=30)

    # First enrollment
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    # Duplicate
    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    assert response.status_code == 400
    assert "already enrolled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_enroll_full_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="FULL01", capacity=1)

    # First student fills the course
    _, s1_token = await create_user_and_token(
        client, name="S1", email="s1@example.com", role="student"
    )
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(s1_token),
    )

    # Second student should be rejected
    _, s2_token = await create_user_and_token(
        client, name="S2", email="s2@example.com", role="student"
    )
    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(s2_token),
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_enroll_inactive_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="INACT01")

    # Deactivate the course
    await client.patch(
        f"/api/v1/courses/{course['id']}",
        json={"is_active": False},
        headers=auth_headers(admin_token),
    )

    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    assert response.status_code == 400
    assert "not active" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_enroll_as_admin_forbidden(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="ADM01")

    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_enroll_nonexistent_course(client: AsyncClient):
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    response = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": 999},
        headers=auth_headers(student_token),
    )
    assert response.status_code == 404


# ── GET /enrollments/

@pytest.mark.asyncio
async def test_list_own_enrollments_student(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="LST01")

    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )

    response = await client.get(
        "/api/v1/enrollments/",
        headers=auth_headers(student_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["course_id"] == course["id"]


@pytest.mark.asyncio
async def test_admin_list_all_enrollments(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, code="ALL01")

    # Two students enroll
    _, s1_token = await create_user_and_token(
        client, name="S1", email="s1@example.com", role="student"
    )
    _, s2_token = await create_user_and_token(
        client, name="S2", email="s2@example.com", role="student"
    )
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(s1_token),
    )
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(s2_token),
    )

    response = await client.get(
        "/api/v1/enrollments/",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_admin_filter_enrollments_by_course(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course_a = await create_test_course(client, admin_token, code="FLTA")
    course_b = await create_test_course(client, admin_token, code="FLTB")

    _, s1_token = await create_user_and_token(
        client, name="S1", email="s1@example.com", role="student"
    )
    # Enroll in both courses
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course_a["id"]},
        headers=auth_headers(s1_token),
    )
    await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course_b["id"]},
        headers=auth_headers(s1_token),
    )

    # Filter by course_a
    response = await client.get(
        f"/api/v1/enrollments/?course_id={course_a['id']}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["course_id"] == course_a["id"]


# ── DELETE /enrollments/{id}

@pytest.mark.asyncio
async def test_deregister_own_enrollment(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="DRG01")

    enroll_resp = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    enrollment_id = enroll_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers=auth_headers(student_token),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_deregister_other_student_forbidden(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, s1_token = await create_user_and_token(
        client, name="S1", email="s1@example.com", role="student"
    )
    _, s2_token = await create_user_and_token(
        client, name="S2", email="s2@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="OTH01")

    enroll_resp = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(s1_token),
    )
    enrollment_id = enroll_resp.json()["id"]

    # S2 tries to delete S1's enrollment
    response = await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers=auth_headers(s2_token),
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_remove_enrollment(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    _, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="ARM01")

    enroll_resp = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    enrollment_id = enroll_resp.json()["id"]

    response = await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_remove_nonexistent_enrollment(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    response = await client.delete(
        "/api/v1/enrollments/999",
        headers=auth_headers(admin_token),
    )
    assert response.status_code == 404
