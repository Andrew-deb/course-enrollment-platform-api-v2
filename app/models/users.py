from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db_async import Base

if TYPE_CHECKING:
    from app.models.enrollments import Enrollment


class User(Base):
    __tablename__ = "users"

    id:              Mapped[int]  = mapped_column(primary_key=True, autoincrement=True)
    name:            Mapped[str]  = mapped_column(String(100))
    email:           Mapped[str]  = mapped_column(String(150), unique=True, index=True)
    hashed_password: Mapped[str]  = mapped_column(String(255))
    role:            Mapped[str]  = mapped_column(String(20), default="student")
    is_active:       Mapped[bool] = mapped_column(default=True)

    # One-to-Many: user has many enrollments
    enrollments: Mapped[list["Enrollment"]] = relationship(
        "Enrollment", back_populates="student", lazy="selectin"
    )
