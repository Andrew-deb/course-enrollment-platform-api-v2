from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.courses import Course
from app.schemas.courses import CourseCreate, CourseUpdate, CoursePatch


class CourseRepository:
    """All Course database operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
        result = await db.execute(
            select(Course).where(Course.id == course_id, Course.deleted_at.is_(None))
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Course | None:
        result = await db.execute(
            select(Course).where(Course.code == code, Course.deleted_at.is_(None))
        )
        return result.scalars().first()

    @staticmethod
    async def get_all_active(
        db: AsyncSession, skip: int = 0, limit: int = 20, title: str | None = None
    ) -> list[Course]:
        stmt = select(Course).where(Course.is_active == True, Course.deleted_at.is_(None))
        if title:
            stmt = stmt.where(Course.title.ilike(f"%{title}%"))
        stmt = stmt.order_by(Course.id).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_active(db: AsyncSession, title: str | None = None) -> int:
        stmt = select(func.count(Course.id)).where(
            Course.is_active == True, Course.deleted_at.is_(None)
        )
        if title:
            stmt = stmt.where(Course.title.ilike(f"%{title}%"))
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        course = Course(
            title=data.title,
            code=data.code,
            capacity=data.capacity,
        )
        db.add(course)
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def update(db: AsyncSession, course: Course, data: CourseUpdate) -> Course:
        course.title = data.title
        course.code = data.code
        course.capacity = data.capacity
        course.is_active = data.is_active
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def patch(db: AsyncSession, course: Course, data: CoursePatch) -> Course:
        fields = data.model_dump(exclude_unset=True)
        for key, value in fields.items():
            setattr(course, key, value)
        await db.flush()
        await db.refresh(course)
        return course

    @staticmethod
    async def delete(db: AsyncSession, course: Course) -> None:
        course.deleted_at = func.now()
        await db.flush()

