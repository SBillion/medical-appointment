from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbDep
from app.core.exceptions import SlotAlreadyBookedError, SlotUnavailableError
from app.schemas import (
    AppointmentSlotOut,
    BookingOut,
    BookingRequest,
    DoctorOut,
    ErrorOut,
)
from app.services import book_slot, list_available_slots

router = APIRouter()


@router.get(
    "/slots",
    response_model=list[AppointmentSlotOut],
    summary="List available appointment slots",
    description=(
        "Returns all unbooked appointment slots aggregated by start time.\n\n"
        "Each slot includes the number of doctors still available at that "
        "time. Slots that are fully booked are excluded entirely. Results are "
        "ordered chronologically by start time."
    ),
)
async def get_slots(db: DbDep) -> list[AppointmentSlotOut]:
    return [
        AppointmentSlotOut(
            starts_at=slot["starts_at"],
            available_doctors=slot["available_doctors"],
        )
        for slot in await list_available_slots(db)
    ]


@router.post(
    "/bookings",
    response_model=BookingOut,
    status_code=status.HTTP_201_CREATED,
    summary="Book an appointment",
    description=(
        "Books one available doctor for the requested start time.\n\n"
        "The caller does **not** choose a doctor — the backend selects one "
        "automatically using row-level locking "
        "(`SELECT ... FOR UPDATE SKIP LOCKED`) to prevent double-booking "
        "under concurrent requests. A unique constraint on "
        "`appointments.doctor_availability_id` is the final backstop.\n\n"
        "If all doctors for that slot have been booked, returns `409`. If no "
        "availability ever existed for that time, returns `404`."
    ),
    responses={
        404: {"model": ErrorOut, "description": "No availability for this slot"},
        409: {"model": ErrorOut, "description": "Slot no longer available"},
    },
)
async def create_booking(payload: BookingRequest, db: DbDep) -> BookingOut:
    try:
        appointment = await book_slot(db, payload.starts_at)
    except SlotUnavailableError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No availability for the requested slot.",
        ) from None
    except SlotAlreadyBookedError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The selected slot is no longer available.",
        ) from None
    availability = appointment.availability
    return BookingOut(
        id=appointment.id,
        starts_at=availability.starts_at,
        ends_at=availability.ends_at,
        doctor=DoctorOut.model_validate(availability.doctor),
    )
