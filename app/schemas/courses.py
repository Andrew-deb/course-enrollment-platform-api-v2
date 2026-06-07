from pydantic import BaseModel, ConfigDict, Field


class CourseCreate(BaseModel):
    title: str
    code: str
    capacity: int = Field(gt=0)


class CourseUpdate(BaseModel):
    title: str
    code: str
    capacity: int = Field(gt=0)
    is_active: bool


class CoursePatch(BaseModel):
    title: str | None = None
    code: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    is_active: bool | None = None


class CourseRead(BaseModel):
    id: int
    title: str
    code: str
    capacity: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
