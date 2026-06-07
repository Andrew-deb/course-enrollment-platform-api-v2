from sqlalchemy.ext.asyncio import AsyncSession

from app.models.audit_logs import EnrollmentAuditLog
from app.repositories.audit_log_repository import AuditLogRepository


class AuditLogService:

    @staticmethod
    async def get_audit_logs(
        db: AsyncSession, skip: int = 0, limit: int = 20
    ) -> tuple[list[EnrollmentAuditLog], int]:
        items = await AuditLogRepository.get_all(db, skip=skip, limit=limit)
        total = await AuditLogRepository.count(db)
        return items, total
