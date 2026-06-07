from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.courses import Course
from app.repositories.course_repository import CourseRepository
from app.schemas.courses import CourseCreate, CourseUpdate, CoursePatch


class CourseService:

    @staticmethod
    async def get_all_active(db: AsyncSession) -> list[Course]:
        return await CourseRepository.get_all_active(db)

    @staticmethod
    async def get_by_id(db: AsyncSession, course_id: int) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        return course

    @staticmethod
    async def create(db: AsyncSession, data: CourseCreate) -> Course:
        if await CourseRepository.get_by_code(db, data.code):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course code already exists",
            )
        return await CourseRepository.create(db, data)

    @staticmethod
    async def update(
        db: AsyncSession, course_id: int, data: CourseUpdate
    ) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        # If code is changing, check uniqueness
        if data.code != course.code:
            if await CourseRepository.get_by_code(db, data.code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course code already exists",
                )
        return await CourseRepository.update(db, course, data)

    @staticmethod
    async def patch(
        db: AsyncSession, course_id: int, data: CoursePatch
    ) -> Course:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        # If code is being changed, check uniqueness
        if data.code is not None and data.code != course.code:
            if await CourseRepository.get_by_code(db, data.code):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Course code already exists",
                )
        return await CourseRepository.patch(db, course, data)

    @staticmethod
    async def delete(db: AsyncSession, course_id: int) -> None:
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )
        await CourseRepository.delete(db, course)
