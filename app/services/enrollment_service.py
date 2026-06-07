from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enrollments import Enrollment
from app.models.users import User
from app.repositories.course_repository import CourseRepository
from app.repositories.enrollment_repository import EnrollmentRepository


class EnrollmentService:

    @staticmethod
    async def enroll(
        db: AsyncSession, course_id: int, current_user: User
    ) -> Enrollment:
        # 1. Check course exists
        course = await CourseRepository.get_by_id(db, course_id)
        if not course:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Course not found",
            )

        # 2. Check course is active
        if not course.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is not active",
            )

        # 3. Check duplicate enrollment
        existing = await EnrollmentRepository.get_by_user_and_course(
            db, current_user.id, course_id
        )
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Already enrolled in this course",
            )

        # 4. Check capacity
        current_count = await EnrollmentRepository.count_by_course(db, course_id)
        if current_count >= course.capacity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Course is full",
            )

        # 5. Create enrollment
        return await EnrollmentRepository.create(db, current_user.id, course_id)

    @staticmethod
    async def deregister(
        db: AsyncSession, enrollment_id: int, current_user: User
    ) -> None:
        enrollment = await EnrollmentRepository.get_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        if enrollment.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not your enrollment",
            )
        await EnrollmentRepository.delete(db, enrollment)

    @staticmethod
    async def get_student_enrollments(
        db: AsyncSession, user_id: int
    ) -> list[Enrollment]:
        return await EnrollmentRepository.get_by_user(db, user_id)

    @staticmethod
    async def get_all_enrollments(
        db: AsyncSession, course_id: int | None = None
    ) -> list[Enrollment]:
        return await EnrollmentRepository.get_all(db, course_id=course_id)

    @staticmethod
    async def admin_remove(db: AsyncSession, enrollment_id: int) -> None:
        enrollment = await EnrollmentRepository.get_by_id(db, enrollment_id)
        if not enrollment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Enrollment not found",
            )
        await EnrollmentRepository.delete(db, enrollment)
