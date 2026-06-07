# Course Enrollment Platform API

A secure, database-backed RESTful API built with FastAPI for managing a course enrollment platform. Features JWT authentication, role-based access control (student/admin), and comprehensive automated tests.

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL (async via asyncpg)
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
# - DATABASE_URL and DATABASE_URL_ASYNC (your PostgreSQL connection strings)
```

### 5. Create the PostgreSQL database

```bash
createdb course_enrollment
# Or via psql:
# psql -U postgres -c "CREATE DATABASE course_enrollment;"
```

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
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Running Tests

```bash
# Run all tests
pytest app/tests/ -v

# Run specific test file
pytest app/tests/api/test_auth.py -v
pytest app/tests/api/test_courses.py -v
pytest app/tests/api/test_enrollments.py -v
```

Tests use an in-memory SQLite database, so no external database setup is needed for testing.

## API Endpoints

### Authentication
| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/register` | Register a new user |
| POST | `/api/v1/auth/token` | Login and get JWT token |
| GET | `/api/v1/auth/me` | Get current user profile |

### Courses
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/api/v1/courses/` | Public | List all active courses |
| GET | `/api/v1/courses/{id}` | Public | Get course by ID |
| POST | `/api/v1/courses/` | Admin | Create a new course |
| PUT | `/api/v1/courses/{id}` | Admin | Update a course |
| PATCH | `/api/v1/courses/{id}` | Admin | Partially update a course |
| DELETE | `/api/v1/courses/{id}` | Admin | Delete a course |

### Enrollments
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/enrollments/` | Student | Enroll in a course |
| GET | `/api/v1/enrollments/` | Student/Admin | List enrollments |
| DELETE | `/api/v1/enrollments/{id}` | Student/Admin | Remove enrollment |
