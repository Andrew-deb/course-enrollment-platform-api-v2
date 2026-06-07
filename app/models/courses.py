from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.enrollments import Enrollment


class Course(Base):
    __tablename__ = "courses"

    id:        Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    title:     Mapped[str]  = mapped_column(String(200))
    code:      Mapped[str]  = mapped_column(String(20), unique=True, index=True)
    capacity:  Mapped[int]  = mapped_column()
    is_active: Mapped[bool] = mapped_column(default=True)

    # One-to-Many: course has many enrollments
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="course", lazy="selectin"
    )
