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
            .where(Enrollment.id == enrollment_id, Enrollment.deleted_at.is_(None))
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
                Enrollment.deleted_at.is_(None),
            )
        )
        return result.scalars().first()

    @staticmethod
    async def get_by_user(
        db: AsyncSession, user_id: int, skip: int = 0, limit: int = 20
    ) -> list[Enrollment]:
        result = await db.execute(
            select(Enrollment)
            .where(Enrollment.user_id == user_id, Enrollment.deleted_at.is_(None))
            .order_by(Enrollment.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count_by_user(db: AsyncSession, user_id: int) -> int:
        result = await db.execute(
            select(func.count(Enrollment.id)).where(
                Enrollment.user_id == user_id, Enrollment.deleted_at.is_(None)
            )
        )
        return result.scalar_one()

    @staticmethod
    async def get_all(
        db: AsyncSession, course_id: int | None = None, skip: int = 0, limit: int = 20
    ) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.deleted_at.is_(None)).order_by(Enrollment.created_at.desc())
        if course_id is not None:
            stmt = stmt.where(Enrollment.course_id == course_id)
        stmt = stmt.offset(skip).limit(limit)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def count_all(db: AsyncSession, course_id: int | None = None) -> int:
        stmt = select(func.count(Enrollment.id)).where(Enrollment.deleted_at.is_(None))
        if course_id is not None:
            stmt = stmt.where(Enrollment.course_id == course_id)
        result = await db.execute(stmt)
        return result.scalar_one()

    @staticmethod
    async def count_by_course(db: AsyncSession, course_id: int) -> int:
        result = await db.execute(
            select(func.count()).select_from(Enrollment).where(
                Enrollment.course_id == course_id,
                Enrollment.deleted_at.is_(None)
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
        enrollment.deleted_at = func.now()
        await db.flush()

