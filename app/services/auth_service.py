from datetime import timedelta

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.models.users import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import Token
from app.schemas.users import UserCreate

VALID_ROLES = {"student", "admin"}


class AuthService:

    @staticmethod
    async def register(db: AsyncSession, data: UserCreate) -> User:
        if data.role not in VALID_ROLES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}",
            )

        if await UserRepository.get_by_email(db, data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = await UserRepository.create(db, data)
        return user

    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> Token:
        user = await UserRepository.get_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Inactive user account",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = create_access_token(
            data={"sub": user.email, "role": user.role},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=token, token_type="bearer")
