"""Integration tests for POST /api/bookings."""

import pytest
from sqlalchemy import select

from app.models import Appointment
from tests.factories import (
    booking_payload,
    insert_availability,
    insert_doctors,
    utc,
)


async def test_booking_succeeds_and_returns_doctor(client, db):
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)
    await insert_availability(db, doctors[1], slot)

    response = await client.post("/api/bookings", json=booking_payload(slot))

    assert response.status_code == 201
    body = response.json()
    assert body["startsAt"] == slot.strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["endsAt"] == (slot.replace(minute=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
    assert body["doctor"]["id"] in [d.id for d in doctors]
    assert body["doctor"]["fullName"] in {"Dr. Hart", "Dr. Silva"}


async def test_booking_persists_appointment(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)

    response = await client.post("/api/bookings", json=booking_payload(slot))
    assert response.status_code == 201

    db.expire_all()
    appts = (await db.execute(select(Appointment))).scalars().all()
    assert len(appts) == 1


async def test_booking_unknown_slot_returns_404(client, db):
    await insert_doctors(db, [("Dr. Hart", "General Medicine")])

    response = await client.post("/api/bookings", json=booking_payload(utc(10, 0)))
    assert response.status_code == 404
    assert "detail" in response.json()


async def test_booking_reduces_slot_count(client, db):
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)
    await insert_availability(db, doctors[1], slot)

    booking = await client.post("/api/bookings", json=booking_payload(slot))
    assert booking.status_code == 201

    slots = await client.get("/api/slots")
    assert slots.json() == [
        {"startsAt": slot.strftime("%Y-%m-%dT%H:%M:%SZ"), "availableDoctors": 1}
    ]


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"startsAt": "not-a-date"},
    ],
    ids=["empty", "invalid-date"],
)
async def test_invalid_payload_returns_422(client, payload):
    response = await client.post("/api/bookings", json=payload)
    assert response.status_code == 422


async def test_booking_past_slot_returns_422(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    past_slot = utc(10, 0, day_offset=-1)
    await insert_availability(db, doctors[0], past_slot)

    response = await client.post("/api/bookings", json=booking_payload(past_slot))
    assert response.status_code == 422
    assert "past" in response.json()["detail"][0]["msg"].lower()


async def test_double_booking_single_doctor_returns_409(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)

    first = await client.post("/api/bookings", json=booking_payload(slot))
    assert first.status_code == 201

    second = await client.post("/api/bookings", json=booking_payload(slot))
    assert second.status_code == 409
    assert "detail" in second.json()


async def test_double_booking_exhausts_slot_then_conflicts(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)

    await client.post("/api/bookings", json=booking_payload(slot))
    response = await client.get("/api/slots")
    assert response.json() == []
