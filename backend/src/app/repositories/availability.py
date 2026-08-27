from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Appointment, DoctorAvailability


class AvailabilityRepository:
    """Reads and locks doctor availability rows."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def list_unbooked_grouped_by_start(self) -> list[tuple[datetime, int]]:
        """Return (starts_at, count) for all unbooked availabilities, ordered
        chronologically."""
        booked_ids = select(Appointment.doctor_availability_id)
        stmt = (
            select(
                DoctorAvailability.starts_at,
                func.count(DoctorAvailability.id).label("available_doctors"),
            )
            .where(~DoctorAvailability.id.in_(booked_ids))
            .group_by(DoctorAvailability.starts_at)
            .order_by(DoctorAvailability.starts_at)
        )
        rows = (await self._db.execute(stmt)).all()
        return [(row.starts_at, row.available_doctors) for row in rows]

    async def find_bookable(self, starts_at: datetime) -> DoctorAvailability | None:
        """Find and lock one unbooked availability for the given start time.

        Uses SELECT ... FOR UPDATE SKIP LOCKED so concurrent requests for the
        same slot don't block each other; skipped rows are simply ignored.
        """
        stmt = (
            select(DoctorAvailability)
            .options(selectinload(DoctorAvailability.doctor))
            .where(DoctorAvailability.starts_at == starts_at)
            .where(
                ~DoctorAvailability.id.in_(select(Appointment.doctor_availability_id))
            )
            .order_by(DoctorAvailability.id)
            .limit(1)
            .with_for_update(skip_locked=True)
        )
        return (await self._db.execute(stmt)).scalars().first()

    async def exists_for_start(self, starts_at: datetime) -> bool:
        """Check whether any availability exists for the given start time,
        regardless of booking status."""
        row = (
            await self._db.execute(
                select(DoctorAvailability.id).where(
                    DoctorAvailability.starts_at == starts_at
                )
            )
        ).first()
        return row is not None
