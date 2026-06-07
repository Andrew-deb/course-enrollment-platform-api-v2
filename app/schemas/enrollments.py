from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime
    deleted_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class PaginatedEnrollments(BaseModel):
    items: list[EnrollmentRead]
    total: int
    skip: int
    limit: int


class AuditLogRead(BaseModel):
    id: int
    user_id: int | None
    enrollment_id: int
    action: str
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedAuditLogs(BaseModel):
    items: list[AuditLogRead]
    total: int
    skip: int
    limit: int

