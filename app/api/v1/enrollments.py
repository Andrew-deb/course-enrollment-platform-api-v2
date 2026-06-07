from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_active_user, require_student
from app.models.users import User
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollments import EnrollmentCreate, EnrollmentRead

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


@router.get("/", response_model=list[EnrollmentRead])
async def list_enrollments(
    course_id: int | None = Query(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "admin":
        return await EnrollmentService.get_all_enrollments(db, course_id=course_id)
    # Students see only their own enrollments
    return await EnrollmentService.get_student_enrollments(db, current_user.id)


@router.delete("/{enrollment_id}", status_code=200)
async def remove_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role == "admin":
        await EnrollmentService.admin_remove(db, enrollment_id)
    else:
        await EnrollmentService.deregister(db, enrollment_id, current_user)
    await db.commit()
    return {"detail": "Enrollment removed"}
