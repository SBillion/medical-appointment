"""Integration tests for GET /api/slots."""

import pytest

from tests.factories import book, insert_availability, insert_doctors, utc


async def test_empty_when_no_availabilities(client):
    response = await client.get("/api/slots")
    assert response.status_code == 200
    assert response.json() == []


async def test_aggregates_slots_by_start_time(client, db):
    doctors = await insert_doctors(
        db,
        [
            ("Dr. Hart", "General Medicine"),
            ("Dr. Silva", "General Medicine"),
            ("Dr. Moreau", "Sleep Medicine"),
        ],
    )

    slot = utc(10, 0)
    for doctor in doctors:
        await insert_availability(db, doctor, slot)

    response = await client.get("/api/slots")
    assert response.status_code == 200
    assert response.json() == [
        {"startsAt": "2026-01-01T10:00:00Z", "availableDoctors": 3}
    ]


async def test_keeps_separate_slots_separate(client, db):
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    await insert_availability(db, doctors[0], utc(10, 0))
    await insert_availability(db, doctors[1], utc(10, 30))

    response = await client.get("/api/slots")
    body = sorted(response.json(), key=lambda s: s["startsAt"])
    assert body == [
        {"startsAt": "2026-01-01T10:00:00Z", "availableDoctors": 1},
        {"startsAt": "2026-01-01T10:30:00Z", "availableDoctors": 1},
    ]


@pytest.mark.parametrize(
    ("booked_count", "expected_available"),
    [(0, 2), (1, 1), (2, 0)],
    ids=["none-booked", "partially-booked", "fully-booked"],
)
async def test_slot_availability_decreases_as_booked(
    client, db, booked_count, expected_available
):
    """Slots should reflect the number of unbooked doctors."""
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    slot = utc(10, 0)
    avails = [await insert_availability(db, d, slot) for d in doctors]

    for i in range(booked_count):
        await book(db, avails[i])

    response = await client.get("/api/slots")

    if expected_available == 0:
        assert response.json() == []
    else:
        assert response.json() == [
            {
                "startsAt": "2026-01-01T10:00:00Z",
                "availableDoctors": expected_available,
            }
        ]


async def test_slots_are_sorted_chronologically(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    await insert_availability(db, doctors[0], utc(16, 0))
    await insert_availability(db, doctors[0], utc(10, 0))
    await insert_availability(db, doctors[0], utc(12, 0))

    response = await client.get("/api/slots")
    starts = [s["startsAt"] for s in response.json()]
    assert starts == [
        "2026-01-01T10:00:00Z",
        "2026-01-01T12:00:00Z",
        "2026-01-01T16:00:00Z",
    ]
