from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1 import auth, courses, enrollments

# ── 1. App instance 
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── 2. Middleware 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 3. Routers 
app.include_router(auth.router,        prefix=settings.API_V1_PREFIX)
app.include_router(courses.router,     prefix=settings.API_V1_PREFIX)
app.include_router(enrollments.router, prefix=settings.API_V1_PREFIX)
