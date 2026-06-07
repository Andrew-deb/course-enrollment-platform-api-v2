from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_active_user
from app.services.auth_service import AuthService
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserRead, status_code=201)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    user = await AuthService.register(db, data)
    await db.commit()
    return user


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    return await AuthService.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_active_user)):
    return current_user
