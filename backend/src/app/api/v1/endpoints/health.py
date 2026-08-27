from fastapi import APIRouter
from sqlalchemy import text

from app.api.deps import DbDep

router = APIRouter()


@router.get(
    "/health",
    summary="Health check",
    description="Verifies the database connection is alive by executing `SELECT 1`.",
)
async def healthcheck(db: DbDep) -> dict[str, str]:
    await db.execute(text("SELECT 1"))
    return {"status": "ok"}
