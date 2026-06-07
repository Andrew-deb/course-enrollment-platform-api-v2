from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_active_user, require_student, require_admin
from app.models.users import User
from app.services.enrollment_service import EnrollmentService
from app.services.audit_log_service import AuditLogService
from app.schemas.enrollments import (
    EnrollmentCreate,
    EnrollmentRead,
    PaginatedEnrollments,
    PaginatedAuditLogs,
)

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentRead, status_code=201)
async def enroll(
    data: EnrollmentCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_student),
):
    enrollment = await EnrollmentService.enroll(db, data.course_id, current_user)
    await db.commit()
    return enrollment


@router.get("/", response_model=PaginatedEnrollments)
async def list_enrollments(
    course_id: int | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "admin":
        items, total = await EnrollmentService.get_all_enrollments(
            db, course_id=course_id, skip=skip, limit=limit
        )
    else:
        # Students see only their own enrollments
        items, total = await EnrollmentService.get_student_enrollments(
            db, current_user.id, skip=skip, limit=limit
        )
    return {"items": items, "total": total, "skip": skip, "limit": limit}


@router.delete("/{enrollment_id}", status_code=200)
async def remove_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "admin":
        await EnrollmentService.admin_remove(db, enrollment_id, current_user)
    else:
        await EnrollmentService.deregister(db, enrollment_id, current_user)
    await db.commit()
    return {"detail": "Enrollment removed"}


@router.get("/audit-logs/", response_model=PaginatedAuditLogs)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(require_admin),
):
    items, total = await AuditLogService.get_audit_logs(db, skip=skip, limit=limit)
    return {"items": items, "total": total, "skip": skip, "limit": limit}

