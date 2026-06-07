import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.db_async import Base
from app.core.deps import get_async_db
from app.core.security import hash_password
from app.main import app
from app.models.users import User
from app.models.courses import Course

# ── Test database (async SQLite in-memory) 

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


# ── Fixtures

@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(autouse=True)
async def setup_database():
    """Create all tables before each test, drop after."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an httpx AsyncClient with the test DB session injected."""
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_async_db] = override_get_db
    app.state.limiter.enabled = False
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Helper functions

async def create_user(
    client: AsyncClient,
    name: str = "Test User",
    email: str = "test@example.com",
    password: str = "password123",
    role: str = "student",
) -> dict:
    """Register a user and return the response JSON."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"name": name, "email": email, "password": password, "role": role},
    )
    return response.json()


async def get_token(
    client: AsyncClient,
    email: str = "test@example.com",
    password: str = "password123",
) -> str:
    """Login and return the access token."""
    response = await client.post(
         "/api/v1/auth/token",
         data={"email": email, "password": password},
     )
    return response.json()["access_token"]


async def create_user_and_token(
    client: AsyncClient,
    name: str = "Test User",
    email: str = "test@example.com",
    password: str = "password123",
    role: str = "student",
) -> tuple[dict, str]:
    """Register a user and return (user_data, token)."""
    user_data = await create_user(client, name, email, password, role)
    token = await get_token(client, email, password)
    return user_data, token


def auth_headers(token: str) -> dict:
    """Build Authorization header dict."""
    return {"Authorization": f"Bearer {token}"}


async def create_test_course(
    client: AsyncClient,
    token: str,
    title: str = "Introduction to Python",
    code: str = "CS101",
    capacity: int = 30,
) -> dict:
    """Create a course as admin and return response JSON."""
    response = await client.post(
        "/api/v1/courses/",
        json={"title": title, "code": code, "capacity": capacity},
        headers=auth_headers(token),
    )
    return response.json()
