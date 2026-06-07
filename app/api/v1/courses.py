from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, require_admin
from app.services.course_service import CourseService
from app.schemas.courses import CourseCreate, CourseUpdate, CoursePatch, CourseRead

router = APIRouter(prefix="/courses", tags=["Courses"])


# ── Public endpoints ───────────────────────────────────────────────────────────

@router.get("/", response_model=list[CourseRead])
async def list_courses(
    db: AsyncSession = Depends(get_async_db),
):
    return await CourseService.get_all_active(db)


@router.get("/{course_id}", response_model=CourseRead)
async def get_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
):
    return await CourseService.get_by_id(db, course_id)


# ── Admin-only endpoints ──────────────────────────────────────────────────────

@router.post("/", response_model=CourseRead, status_code=201)
async def create_course(
    data: CourseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    course = await CourseService.create(db, data)
    await db.commit()
    return course


@router.put("/{course_id}", response_model=CourseRead)
async def update_course(
    course_id: int,
    data: CourseUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    course = await CourseService.update(db, course_id, data)
    await db.commit()
    return course


@router.patch("/{course_id}", response_model=CourseRead)
async def patch_course(
    course_id: int,
    data: CoursePatch,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    course = await CourseService.patch(db, course_id, data)
    await db.commit()
    return course


@router.delete("/{course_id}", status_code=200)
async def delete_course(
    course_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user=Depends(require_admin),
):
    await CourseService.delete(db, course_id)
    await db.commit()
    return {"detail": "Course deleted"}
