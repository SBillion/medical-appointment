from datetime import datetime
from typing import TypedDict

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import SlotAlreadyBookedError, SlotUnavailableError
from app.models import Appointment
from app.repositories import AppointmentRepository, AvailabilityRepository


class SlotSummary(TypedDict):
    starts_at: datetime
    available_doctors: int


async def list_available_slots(db: AsyncSession) -> list[SlotSummary]:
    """Aggregate unbooked availabilities by start time, ordered chronologically."""
    repo = AvailabilityRepository(db)
    rows = await repo.list_unbooked_grouped_by_start()
    return [
        SlotSummary(starts_at=starts_at, available_doctors=count)
        for starts_at, count in rows
    ]


async def book_slot(db: AsyncSession, starts_at: datetime) -> Appointment:
    """Book one available doctor for the given start time.

    Raises:
        SlotUnavailableError: no availability exists for this start time.
        SlotAlreadyBookedError: availability existed but is now fully booked.
    """
    avail_repo = AvailabilityRepository(db)
    appt_repo = AppointmentRepository(db)

    availability = await avail_repo.find_bookable(starts_at)

    if availability is None:
        exists = await avail_repo.exists_for_start(starts_at)
        if exists:
            raise SlotAlreadyBookedError()
        raise SlotUnavailableError()

    appointment = await appt_repo.create(availability)
    try:
        await db.flush()
    except IntegrityError:
        raise SlotAlreadyBookedError() from None

    await db.commit()
    appointment.availability = availability
    return appointment


__all__ = [
    "SlotSummary",
    "list_available_slots",
    "book_slot",
]
