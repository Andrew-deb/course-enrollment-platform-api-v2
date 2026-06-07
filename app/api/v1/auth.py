from fastapi import APIRouter, Depends, Request, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_async_db, get_current_active_user
from app.core.limiter import limiter
from app.services.auth_service import AuthService
from app.schemas.auth import Token
from app.schemas.users import UserCreate, UserRead

router = APIRouter(prefix="/auth", tags=["Authentication"])


class OAuth2EmailRequestForm:
    """Custom OAuth2 password request form accepting email or username (for Swagger Authorize compatibility)."""
    def __init__(
        self,
        email: str | None = Form(default=None, description="The user's email address"),
        username: str | None = Form(default=None, description="The user's email address (OAuth2 standard username)"),
        password: str = Form(..., description="The user's password"),
    ):
        self.username = email or username
        self.password = password


@router.post("/register", response_model=UserRead, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    data: UserCreate,
    db: AsyncSession = Depends(get_async_db),
):
    user = await AuthService.register(db, data)
    await db.commit()
    return user


@router.post("/token", response_model=Token)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2EmailRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
):
    return await AuthService.login(db, form_data.username, form_data.password)


@router.get("/me", response_model=UserRead)
async def me(current_user=Depends(get_current_active_user)):
    return current_user

