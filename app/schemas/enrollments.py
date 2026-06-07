from datetime import datetime
from pydantic import BaseModel, ConfigDict


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentRead(BaseModel):
    id: int
    user_id: int
    course_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
