from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.models.enrollments import Enrollment


class EnrollmentRepository:
    """All Enrollment database operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, enrollment_id: int) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.id == enrollment_id)
            .options(selectinload(Enrollment.student), selectinload(Enrollment.course))
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_user_and_course(
        db: AsyncSession, user_id: int, course_id: int
    ) -> Enrollment | None:
        result = await db.execute(
            select(Enrollment).where(
                Enrollment.user_id == user_id,
                Enrollment.course_id == course_id,
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: int) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.user_id == user_id)
            .order_by(Enrollment.created_at.desc())
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_all(
        db: AsyncSession, course_id: int | None = None
    ) -> list[Enrollment]:
        stmt = select(Enrollment).order_by(Enrollment.created_at.desc())
        if course_id is not None:
            stmt = stmt.where(Enrollment.course_id == course_id)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_by_course(db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(Enrollment).where(
                Enrollment.course_id == course_id
            )
        )
        return result.scalar()

    @staticmethod
    async def create(db: AsyncSession, user_id: int, course_id: int) -> Enrollment:
        enrollment = Enrollment(user_id=user_id, course_id=course_id)
        db.add(enrollment)
        await db.flush()
        await db.refresh(enrollment)
        return enrollment

    @staticmethod
    async def delete(db: AsyncSession, enrollment: Enrollment) -> None:
        await db.delete(enrollment)
        await db.flush()
