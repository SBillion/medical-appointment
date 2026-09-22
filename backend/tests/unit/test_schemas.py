"""Unit tests: pure logic with no database or network dependencies."""

from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.schemas import AppointmentSlotOut, BookingOut, BookingRequest

# --- BookingRequest ---


def test_booking_request_parses_iso_with_z_suffix():
    future = datetime.now(UTC) + timedelta(days=1)
    req = BookingRequest(starts_at=future.strftime("%Y-%m-%dT%H:%M:%SZ"))
    assert req.starts_at == future.replace(microsecond=0)


def test_booking_request_rejects_missing_starts_at():
    with pytest.raises(ValidationError):
        BookingRequest()


def test_booking_request_rejects_past_start_time():
    past = datetime.now(UTC) - timedelta(hours=1)
    with pytest.raises(ValidationError) as exc_info:
        BookingRequest(starts_at=past)
    assert "past" in str(exc_info.value).lower()


def test_booking_request_accepts_future_start_time():
    future = datetime.now(UTC) + timedelta(hours=1)
    req = BookingRequest(starts_at=future)
    assert req.starts_at == future


# --- AppointmentSlotOut ---


@pytest.mark.parametrize(
    ("dt", "expected"),
    [
        (datetime(2026, 1, 1, 10, 0, tzinfo=UTC), "2026-01-01T10:00:00Z"),
        (datetime(2026, 1, 1, 23, 59, tzinfo=UTC), "2026-01-01T23:59:00Z"),
        (datetime(2026, 1, 1, 0, 0, tzinfo=UTC), "2026-01-01T00:00:00Z"),
    ],
    ids=["morning", "end-of-day", "midnight"],
)
def test_appointment_slot_out_serializes_starts_at_with_z_suffix(dt, expected):
    slot = AppointmentSlotOut(starts_at=dt, available_doctors=1)
    assert slot.model_dump()["starts_at"] == expected


def test_appointment_slot_out_serializes_naive_datetime_as_utc():
    slot = AppointmentSlotOut(
        starts_at=datetime(2026, 1, 1, 10, 0), available_doctors=1
    )
    assert slot.model_dump()["starts_at"] == "2026-01-01T10:00:00Z"


@pytest.mark.parametrize(
    "invalid_count", [-1, -100], ids=["minus-one", "large-negative"]
)
def test_appointment_slot_out_rejects_negative_doctor_count(invalid_count):
    with pytest.raises(ValidationError):
        AppointmentSlotOut(
            starts_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
            available_doctors=invalid_count,
        )


# --- BookingOut ---


def test_booking_out_serializes_datetimes_with_z_suffix():
    booking = BookingOut(
        id=1,
        starts_at=datetime(2026, 1, 1, 10, 0, tzinfo=UTC),
        ends_at=datetime(2026, 1, 1, 10, 30, tzinfo=UTC),
        doctor={"id": 1, "full_name": "Dr. Hart", "specialty": "General Medicine"},
    )
    dumped = booking.model_dump()
    assert dumped["starts_at"] == "2026-01-01T10:00:00Z"
    assert dumped["ends_at"] == "2026-01-01T10:30:00Z"
    assert dumped["doctor"]["full_name"] == "Dr. Hart"
