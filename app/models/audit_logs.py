from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.users import User


class EnrollmentAuditLog(Base):
    __tablename__ = "enrollment_audit_logs"

    id:            Mapped[int]             = mapped_column(primary_key=True, autoincrement=True)
    user_id:       Mapped[int | None]      = mapped_column(ForeignKey("users.id"), nullable=True)
    enrollment_id: Mapped[int]             = mapped_column(ForeignKey("enrollments.id"))
    action:        Mapped[str]             = mapped_column(String(30)) # ENROLL | DEREGISTER | ADMIN_REMOVE
    timestamp:     Mapped[datetime]         = mapped_column(server_default=func.now())

    user: Mapped["User"] = relationship("User", lazy="joined")
