from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.audit_logs import EnrollmentAuditLog


class AuditLogRepository:
    """All EnrollmentAuditLog database operations."""

    @staticmethod
    async def create(
        db: AsyncSession, user_id: int | None, enrollment_id: int, action: str
    ) -> EnrollmentAuditLog:
        log = EnrollmentAuditLog(
            user_id=user_id, enrollment_id=enrollment_id, action=action
        )
        db.add(log)
        await db.flush()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_all(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> list[EnrollmentAuditLog]:
        result = await db.execute(
            select(EnrollmentAuditLog)
            .order_by(EnrollmentAuditLog.timestamp.desc(), EnrollmentAuditLog.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    @staticmethod
    async def count(db: AsyncSession) -> int:
        result = await db.execute(select(func.count(EnrollmentAuditLog.id)))
        return result.scalar_one()
