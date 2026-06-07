from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.api.v1 import auth, courses, enrollments

# ── 1. App instance 
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)
app.state.limiter = limiter

# ── 2. Middleware 
app.add_middleware(SlowAPIMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── 3. Exception handlers
@app.exception_handler(RateLimitExceeded)
async def custom_rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": f"Rate limit exceeded: {exc.detail}"}
    )

# ── 4. Routers 
app.include_router(auth.router,        prefix=settings.API_V1_PREFIX)
app.include_router(courses.router,     prefix=settings.API_V1_PREFIX)
app.include_router(enrollments.router, prefix=settings.API_V1_PREFIX)


# ── 5. Custom OpenAPI (Clean Swagger UI)
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    try:
        # Get the token endpoint schema
        token_path = openapi_schema.get("paths", {}).get(f"{settings.API_V1_PREFIX}/auth/token", {})
        post_op = token_path.get("post", {})
        schema = post_op.get("requestBody", {}).get("content", {}).get("application/x-www-form-urlencoded", {}).get("schema", {})
        properties = schema.get("properties", {})
        
        # Hide standard 'username' parameter from Swagger UI
        if "username" in properties:
            del properties["username"]
            
        # Display 'email' and 'password' as required fields in the UI
        schema["required"] = ["email", "password"]
    except Exception:
        pass
    app.openapi_schema = openapi_schema
    return openapi_schema

app.openapi = custom_openapi


