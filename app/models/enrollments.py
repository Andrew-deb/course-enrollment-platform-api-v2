from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.users import User
    from app.models.courses import Course


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_user_course"),
    )

    id:         Mapped[int]      = mapped_column(primary_key=True, autoincrement=True)
    user_id:    Mapped[int]      = mapped_column(ForeignKey("users.id"))
    course_id:  Mapped[int]      = mapped_column(ForeignKey("courses.id"))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    # Relationships
    student: Mapped["User"]   = relationship("User", back_populates="enrollments", lazy="joined")
    course:  Mapped["Course"] = relationship("Course", back_populates="enrollments", lazy="joined")
