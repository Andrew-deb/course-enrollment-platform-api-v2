from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.courses import Course
from app.schemas.courses import CourseCreate, CourseUpdate, CoursePatch


class CourseRepository:
    """All Course database operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
        return await db.get(Course, course_id)

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str) -> Course | None:
        result = await db.execute(select(Course).where(Course.code == code))
        return result.scalars().first()

    @staticmethod
    async def get_all_active(db: AsyncSession) -> list[Course]:
        result = await db.execute(
            select(Course).where(Course.is_active == True).order_by(Course.id)
        )
        return list(result.scalars().all())

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
        await db.delete(course)
        await db.flush()
