from sqlalchemy import select
import pytest
from httpx import AsyncClient
from app.main import app
from app.models.courses import Course
from app.models.enrollments import Enrollment
from app.models.audit_logs import EnrollmentAuditLog
from app.tests.conftest import (
    create_user_and_token,
    create_test_course,
    auth_headers,
)


@pytest.mark.asyncio
async def test_rate_limiting(client: AsyncClient):
    # Enable rate limiting specifically for this test
    app.state.limiter.enabled = True
    try:
        # Make multiple login requests rapidly
        for i in range(5):
            response = await client.post(
                "/api/v1/auth/token",
                data={"email": "test@example.com", "password": "wrongpassword"},
            )
            # Should be 401 Unauthorized
            assert response.status_code == 401

        # The 6th request should exceed the limit
        response = await client.post(
            "/api/v1/auth/token",
            data={"email": "test@example.com", "password": "wrongpassword"},
        )
        assert response.status_code == 429
        assert "rate limit exceeded" in response.json()["detail"].lower()
    finally:
        # Disable rate limiting for other tests
        app.state.limiter.enabled = False


@pytest.mark.asyncio
async def test_course_soft_delete(client: AsyncClient, db_session):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    course = await create_test_course(client, admin_token, title="Soft Delete Course", code="SDC01")

    # Verify course exists
    resp = await client.get(f"/api/v1/courses/{course['id']}")
    assert resp.status_code == 200

    # Delete course as admin
    delete_resp = await client.delete(
        f"/api/v1/courses/{course['id']}",
        headers=auth_headers(admin_token),
    )
    assert delete_resp.status_code == 200

    # Verify public API returns 404 / doesn't show it
    get_resp = await client.get(f"/api/v1/courses/{course['id']}")
    assert get_resp.status_code == 404

    list_resp = await client.get("/api/v1/courses/")
    assert not any(c["id"] == course["id"] for c in list_resp.json()["items"])

    # Query DB directly to check the record is still there but soft deleted
    # We execute in a new transaction context or clear session to ensure we read from DB
    db_session.expire_all()
    result = await db_session.execute(
        select(Course).where(Course.id == course["id"])
    )
    db_course = result.scalars().first()
    assert db_course is not None
    assert db_course.deleted_at is not None


@pytest.mark.asyncio
async def test_enrollment_soft_delete(client: AsyncClient, db_session):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    student_data, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="SD_ENR01")

    # Enroll
    enroll_resp = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    assert enroll_resp.status_code == 201
    enrollment_id = enroll_resp.json()["id"]

    # Deregister (soft delete)
    dereg_resp = await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers=auth_headers(student_token),
    )
    assert dereg_resp.status_code == 200

    # Verify list is empty
    list_resp = await client.get("/api/v1/enrollments/", headers=auth_headers(student_token))
    assert len(list_resp.json()["items"]) == 0

    # Query DB directly to verify soft delete
    db_session.expire_all()
    result = await db_session.execute(
        select(Enrollment).where(Enrollment.id == enrollment_id)
    )
    db_enrollment = result.scalars().first()
    assert db_enrollment is not None
    assert db_enrollment.deleted_at is not None


@pytest.mark.asyncio
async def test_audit_logs(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    student_data, student_token = await create_user_and_token(
        client, name="Student", email="student@example.com", role="student"
    )
    course = await create_test_course(client, admin_token, code="AUD01")

    # 1. Enroll -> creates ENROLL log
    enroll_resp = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    enrollment_id = enroll_resp.json()["id"]

    # 2. Deregister -> creates DEREGISTER log
    await client.delete(
        f"/api/v1/enrollments/{enrollment_id}",
        headers=auth_headers(student_token),
    )

    # 3. Enroll again
    enroll_resp2 = await client.post(
        "/api/v1/enrollments/",
        json={"course_id": course["id"]},
        headers=auth_headers(student_token),
    )
    enrollment_id2 = enroll_resp2.json()["id"]

    # 4. Admin remove -> creates ADMIN_REMOVE log
    await client.delete(
        f"/api/v1/enrollments/{enrollment_id2}",
        headers=auth_headers(admin_token),
    )

    # Fetch audit logs as admin
    audit_resp = await client.get(
        "/api/v1/enrollments/audit-logs/",
        headers=auth_headers(admin_token),
    )
    assert audit_resp.status_code == 200
    logs = audit_resp.json()["items"]
    assert len(logs) == 4

    # Order is descending by timestamp (latest first)
    assert logs[0]["action"] == "ADMIN_REMOVE"
    assert logs[0]["user_id"] is not None # Admin who did it
    assert logs[1]["action"] == "ENROLL"
    assert logs[2]["action"] == "DEREGISTER"
    assert logs[3]["action"] == "ENROLL"


@pytest.mark.asyncio
async def test_courses_pagination_and_filtering(client: AsyncClient):
    _, admin_token = await create_user_and_token(
        client, name="Admin", email="admin@example.com", role="admin"
    )
    # Create 4 courses
    await create_test_course(client, admin_token, title="Intro to Python", code="PY001")
    await create_test_course(client, admin_token, title="Advanced Python", code="PY002")
    await create_test_course(client, admin_token, title="Intro to Go", code="GO001")
    await create_test_course(client, admin_token, title="Java Programming", code="JV001")

    # Test Pagination (limit=2)
    resp = await client.get("/api/v1/courses/?limit=2")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 4
    assert len(data["items"]) == 2
    assert data["limit"] == 2
    assert data["skip"] == 0

    # Test Filtering (title=Python)
    resp = await client.get("/api/v1/courses/?title=python")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2
    assert all("python" in c["title"].lower() for c in data["items"])
