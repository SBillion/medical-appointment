"""Shared test helpers: DB seeders, datetime builders, payload helpers."""

from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Appointment, Doctor, DoctorAvailability


def utc(hour: int, minute: int = 0, day_offset: int = 1) -> datetime:
    """Return a UTC datetime on a future day (default: tomorrow).

    Tests use day_offset relative to *now* so dates are always in the future
    and never trip the past-booking guard.
    """
    base = datetime.now(UTC).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) + timedelta(days=day_offset)
    return base


def booking_payload(starts_at: datetime | str) -> dict:
    if hasattr(starts_at, "isoformat"):
        starts_at = starts_at.isoformat().replace("+00:00", "Z")
    return {"startsAt": starts_at}


async def insert_doctors(
    db: AsyncSession, names: list[tuple[str, str]]
) -> list[Doctor]:
    doctors = [Doctor(full_name=name, specialty=specialty) for name, specialty in names]
    db.add_all(doctors)
    await db.commit()
    for d in doctors:
        await db.refresh(d)
    return doctors


async def insert_availability(
    db: AsyncSession, doctor: Doctor, starts_at: datetime, duration: int = 30
) -> DoctorAvailability:
    avail = DoctorAvailability(
        doctor_id=doctor.id,
        starts_at=starts_at,
        ends_at=starts_at + timedelta(minutes=duration),
    )
    db.add(avail)
    await db.commit()
    await db.refresh(avail)
    return avail


async def book(db: AsyncSession, availability: DoctorAvailability) -> Appointment:
    appt = Appointment(doctor_availability_id=availability.id)
    db.add(appt)
    await db.commit()
    await db.refresh(appt)
    return appt
