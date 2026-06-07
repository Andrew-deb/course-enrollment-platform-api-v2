# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing a course enrollment platform. Features JWT authentication, role-based access control (student/admin), and comprehensive automated tests.

## Tech Stack

- **Framework**: FastAPI
- **Database**: Supabase PostgreSQL (async via asyncpg with connection pooling)
- **ORM**: SQLAlchemy 2.0
- **Migrations**: Alembic
- **Auth**: JWT (python-jose) + bcrypt (passlib)
- **Validation**: Pydantic v2

## Project Structure

```
course-enrollment-platform-api/
├── app/
│   ├── api/v1/          # Route handlers (auth, courses, enrollments)
│   ├── core/            # Config, DB engines, dependencies, security
│   ├── models/          # SQLAlchemy ORM models
│   ├── schemas/         # Pydantic request/response models
│   ├── repositories/    # Database access layer
│   ├── services/        # Business logic layer
│   └── tests/           # Automated test suite
├── alembic/             # Database migrations
├── requirements.txt
└── .env.example
```

## Setup Instructions

### 1. Clone the repository

```bash
git clone <repository-url>
cd course-enrollment-platform-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
# Copy the example env file
cp .env.example .env

# Edit .env and set your values:
# - SECRET_KEY (generate with: python -c "import secrets; print(secrets.token_hex(32))")
# - DATABASE_URL (sync for Alembic on port 5432) and DATABASE_URL_ASYNC (async for FastAPI on port 6543)
```

Using port `5432` on the Supabase pooler host (`*.pooler.supabase.com`) runs PgBouncer in **Session Mode**, which is suitable for schema migration operations and resolves IPv4 hostname connection issues.
Using port `6543` runs PgBouncer in **Transaction Mode**, which is optimal for high-concurrency API performance. To prevent PgBouncer issues in Transaction Mode, the async engine is configured with `statement_cache_size=0` to disable prepared statements.


## Running Migrations

```bash
# Generate a new migration (after model changes)
alembic revision --autogenerate -m "description"

# Apply all migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1
```

## Running the Application

```bash
# Windows (recommended to avoid virtualenv executable path issues)
.\venv\Scripts\python -m uvicorn app.main:app --reload

# macOS/Linux
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000` (locally) and `https://course-enrollment-platform-api-v2.onrender.com` (live).

### Local Links
- **API URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Deployed Live Links
- **API URL**: https://course-enrollment-platform-api-v2.onrender.com
- **Swagger UI**: https://course-enrollment-platform-api-v2.onrender.com/docs

## Running Tests

```bash
# Run all tests (Windows)
.\venv\Scripts\python -m pytest app/tests/ -v

# Run all tests (macOS/Linux)
pytest app/tests/ -v

# Run specific test file (Windows)
.\venv\Scripts\python -m pytest app/tests/api/test_auth.py -v
```

Tests use an in-memory SQLite database, so no external database setup is needed for testing.

## API Endpoints

### Authentication
| Method | Path | Description | Rate Limit |
|--------|------|-------------|------------|
| POST | `/api/v1/auth/register` | Register a new user | 5 requests / min |
| POST | `/api/v1/auth/token` | Login and get JWT token | 5 requests / min |
| GET | `/api/v1/auth/me` | Get current user profile | None |

### Courses
| Method | Path | Auth | Description | Query Parameters |
|--------|------|------|-------------|------------------|
| GET | `/api/v1/courses/` | Public | List active courses (paginated) | `skip` (default 0), `limit` (default 20), `title` (optional string search) |
| GET | `/api/v1/courses/{id}` | Public | Get course by ID | None |
| POST | `/api/v1/courses/` | Admin | Create a new course | None |
| PUT | `/api/v1/courses/{id}` | Admin | Update a course | None |
| PATCH | `/api/v1/courses/{id}` | Admin | Partially update a course | None |
| DELETE | `/api/v1/courses/{id}` | Admin | Delete a course (soft delete) | None |

### Enrollments
| Method | Path | Auth | Description | Query Parameters |
|--------|------|------|-------------|------------------|
| POST | `/api/v1/enrollments/` | Student | Enroll in a course | None |
| GET | `/api/v1/enrollments/` | Student/Admin | List enrollments (paginated) | `skip` (default 0), `limit` (default 20), `course_id` (optional, Admin filter) |
| DELETE | `/api/v1/enrollments/{id}` | Student/Admin | Remove/Deregister enrollment (soft delete) | None |
| GET | `/api/v1/enrollments/audit-logs/` | Admin | View enrollment audit logs (paginated) | `skip` (default 0), `limit` (default 20) |

---

## Optional Extensions (Bonus Features Implemented)

### 1. Pagination & Filtering
- Paginated results returned as:
  ```json
  {
    "items": [...],
    "total": 4,
    "skip": 0,
    "limit": 20
  }
  ```
- Added on `GET /api/v1/courses/` and `GET /api/v1/enrollments/` / `GET /api/v1/enrollments/audit-logs/`.
- Courses support case-insensitive title search parameter: `?title=python`.

### 2. Soft Deletes
- Courses and Enrollments are soft-deleted by setting a `deleted_at` timestamp.
- Soft-deleted courses are hidden from public queries and reject new enrollments.
- Deregistered enrollments are soft-deleted, releasing course capacity slots and satisfying unique constraint validation for future enrollments.

### 3. Audit Logs for Enrollments
- System automatically generates a record in the `enrollment_audit_logs` table for every `"ENROLL"`, `"DEREGISTER"`, and `"ADMIN_REMOVE"` action, tracking the operator `user_id`.
- Admins can query all logs via `GET /api/v1/enrollments/audit-logs/`.

### 4. Rate Limiting on Authentication
- Handled via `slowapi` based on the client IP address.
- Limits register and login routes to 5 requests per minute, returning `429 Too Many Requests` on failure.

