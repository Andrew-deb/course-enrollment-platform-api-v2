from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import User
from app.schemas.users import UserCreate
from app.core.security import hash_password


class UserRepository:
    """All User database operations. Call as UserRepository.method(db, ...)."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
        return await db.get(User, user_id)

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, data: UserCreate) -> User:
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password),
            role=data.role,
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
