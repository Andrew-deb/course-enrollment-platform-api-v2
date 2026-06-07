from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_async import AsyncSessionLocal
from app.core.security import decode_token
from app.models.users import User


# ── Session ────────────────────────────────────────────────────────────────────

async def get_async_db() -> AsyncSession:
    async with AsyncSessionLocal() as db:
        yield db


# ── Auth ───────────────────────────────────────────────────────────────────────

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> User:
    # Import here to avoid circular imports at module level
    from app.repositories.user_repository import UserRepository

    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exc
    except JWTError:
        raise credentials_exc

    user = await UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exc
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


# ── RBAC ───────────────────────────────────────────────────────────────────────

def require_role(*roles: str):
    """Factory — returns a dependency that enforces one of the given roles."""
    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {', '.join(roles)}. You have: {current_user.role}",
            )
        return current_user
    return role_checker


require_admin   = require_role("admin")
require_student = require_role("student")
