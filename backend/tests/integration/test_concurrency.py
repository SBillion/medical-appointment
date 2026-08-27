"""Integration tests: verify double-booking protection under real parallelism.

These require a real Postgres to exercise `SELECT ... FOR UPDATE SKIP LOCKED`
and the unique constraint on appointments.
"""

import asyncio

from tests.factories import booking_payload, insert_availability, insert_doctors, utc


async def test_concurrent_bookings_only_one_succeeds(client, db):
    """Two concurrent booking requests for the same single-doctor slot:
    exactly one must succeed, the other must get 409."""
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)

    responses = await asyncio.gather(
        client.post("/api/bookings", json=booking_payload(slot)),
        client.post("/api/bookings", json=booking_payload(slot)),
    )

    statuses = sorted(r.status_code for r in responses)
    assert statuses == [201, 409]


async def test_concurrent_bookings_two_doctors_both_succeed(client, db):
    """Two concurrent bookings for a two-doctor slot: both succeed, each
    booking a different doctor."""
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    slot = utc(10, 0)
    await insert_availability(db, doctors[0], slot)
    await insert_availability(db, doctors[1], slot)

    responses = await asyncio.gather(
        client.post("/api/bookings", json=booking_payload(slot)),
        client.post("/api/bookings", json=booking_payload(slot)),
    )

    statuses = sorted(r.status_code for r in responses)
    assert statuses == [201, 201]

    doctor_ids = {r.json()["doctor"]["id"] for r in responses}
    assert len(doctor_ids) == 2
