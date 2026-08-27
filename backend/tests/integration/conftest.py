"""Integration test fixtures.

These tests run against the real PostgreSQL instance from `docker compose`.
They require the database service to be running:

    docker compose up -d db

A dedicated test database (configured via `test_database_name` in settings)
is created on first use and kept across the session; tables are truncated
before each test so fixtures start from a clean slate. This exercises the
actual asyncpg driver and Postgres row-level locking
(`SELECT ... FOR UPDATE SKIP LOCKED`) — the exact concurrency behavior the
double-booking logic depends on.
"""

from collections.abc import AsyncGenerator
from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.database import get_db
from app.main import app
from app.settings import settings

REPO_ROOT = Path(__file__).resolve().parents[3]
INIT_DIR = REPO_ROOT / "db" / "init"

# Base server URL (strip the db name) so we can create the test db.
TEST_SERVER_URL = settings.test_database_url.rsplit("/", 1)[0]
TEST_DB_NAME = settings.test_database_name
TEST_DB_URL = f"{TEST_SERVER_URL}/{TEST_DB_NAME}"

# Tables truncated between tests, in dependency order so foreign keys clear.
TRUNCATE_TABLES = ("appointments", "doctor_availabilities", "doctors")


def _split_statements(sql: str) -> list[str]:
    return [
        s.strip()
        for s in sql.split(";")
        if s.strip() and not s.strip().startswith("--")
    ]


async def _apply_schema(conn) -> None:
    """Apply DDL init scripts (skipping the dev seed). Schema uses IF NOT
    EXISTS so re-applying across sessions is idempotent."""
    for script in sorted(INIT_DIR.glob("*.sql")):
        if script.stem.startswith("003_seed"):
            continue
        for stmt in _split_statements(script.read_text()):
            await conn.execute(text(stmt))


async def _ensure_test_database() -> None:
    """Create the test database on the compose server if it doesn't exist."""
    # Connect to the maintenance database ("postgres") to run CREATE DATABASE.
    maint_url = f"{TEST_SERVER_URL}/postgres"
    maint = create_async_engine(maint_url, isolation_level="AUTOCOMMIT")
    try:
        async with maint.connect() as conn:
            exists = (
                await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :name"),
                    {"name": TEST_DB_NAME},
                )
            ).first()
            if not exists:
                await conn.execute(text(f'CREATE DATABASE "{TEST_DB_NAME}"'))
    finally:
        await maint.dispose()


async def _truncate(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE TABLE {', '.join(TRUNCATE_TABLES)} CASCADE"))


@pytest_asyncio.fixture
async def engine() -> AsyncGenerator[AsyncEngine]:
    await _ensure_test_database()
    eng = create_async_engine(TEST_DB_URL, pool_pre_ping=True)
    async with eng.begin() as conn:
        await _apply_schema(conn)
    yield eng
    await eng.dispose()


@pytest_asyncio.fixture
async def session_factory(engine):
    return async_sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


@pytest_asyncio.fixture(autouse=True)
async def _clean_db(engine):
    await _truncate(engine)


@pytest_asyncio.fixture
async def db(session_factory) -> AsyncGenerator[AsyncSession]:
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(session_factory) -> AsyncGenerator[AsyncClient]:
    async def override_get_db() -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
