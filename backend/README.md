<div align="center">

# Backend

FastAPI + SQLAlchemy 2.0 (async) + asyncpg + PostgreSQL

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Tests](https://img.shields.io/badge/tests-38%20passed-brightgreen?logo=pytest&logoColor=white)
![Coverage](https://img.shields.io/badge/coverage-96%25-brightgreen)
![ruff](https://img.shields.io/badge/ruff-passed-brightgreen?logo=ruff&logoColor=white)
![mypy](https://img.shields.io/badge/mypy-strict-blue?logo=python&logoColor=white)

</div>

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) — Python package manager
- [Docker](https://docs.docker.com/get-docker/) (for PostgreSQL)

## Setup

```sh
make install   # uv sync + pre-commit hooks
```

Start the database (from repo root):

```sh
docker compose up -d db
```

## Development

```sh
make dev       # uvicorn with hot reload → http://localhost:8000
```

Interactive API docs available at:

- `http://localhost:8000/docs` — Swagger UI
- `http://localhost:8000/redoc` — ReDoc

## Testing

Tests are split into **unit** (pure logic, no database) and **integration**
(real PostgreSQL, requires `docker compose up -d db`).

```sh
make test               # all tests + coverage
make test-unit          # pure logic only (no Docker needed)
make test-integration   # real PostgreSQL
make test-cov           # coverage HTML report → htmlcov/index.html
```

Coverage threshold: **85%** (enforced via `--cov-fail-under`).

## Code Quality

```sh
make lint       # ruff check
make format     # ruff format
make typecheck  # mypy strict
make check      # lint + typecheck
make clean      # remove caches + coverage artifacts
```

Pre-commit hooks: `ruff`, `ruff-format`, `mypy`, `uv lock check`.

## Architecture

```
src/app/
├── main.py              # FastAPI app + CORS + router
├── settings.py          # Pydantic Settings (env config)
├── api/v1/
│   ├── deps.py          # Shared dependencies (DbDep)
│   ├── router.py        # Router assembly
│   └── endpoints/       # health, appointments
├── core/
│   ├── database.py      # Async engine + session
│   └── exceptions.py    # Domain exceptions
├── models/              # SQLAlchemy ORM models
├── schemas/             # Pydantic V2 request/response schemas
├── repositories/        # Database access layer
└── services/            # Business logic
```

| Layer          | Responsibility                                           |
| -------------- | -------------------------------------------------------- |
| `api/endpoints`| HTTP handlers, request parsing, response serialization  |
| `services`     | Business logic, orchestrates repositories                |
| `repositories` | Database queries (SQLAlchemy), no business rules        |
| `models`       | SQLAlchemy ORM models (tables, relationships)            |
| `schemas`      | Pydantic V2 models (validation, serialization, aliases)  |
| `core`         | Cross-cutting: database engine, exceptions, settings     |

### Double-Booking Prevention

Booking uses `SELECT ... FOR UPDATE SKIP LOCKED` to lock one candidate
availability row, plus a `UNIQUE` constraint on
`appointments.doctor_availability_id` as a database-level backstop. This
guarantees that even under concurrent requests, a single availability
can only be booked once.

## Configuration

All settings via environment variables or `.env` file. See `.env.example`:

| Variable            | Default                                                  |
| ------------------- | -------------------------------------------------------- |
| `DATABASE_URL`      | `postgresql+asyncpg://app:app@localhost:5432/...`      |
| `CORS_ORIGINS`      | `["http://localhost:5173"]`                              |
| `TEST_DATABASE_URL`  | Test Postgres server URL                                 |
| `TEST_DATABASE_NAME` | Test database name (default: `medical_appointment_test`) |