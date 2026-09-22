"""Integration tests for GET /api/slots."""

import pytest

from tests.factories import book, insert_availability, insert_doctors, utc


def iso(dt) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


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
    assert response.json() == [{"startsAt": iso(slot), "availableDoctors": 3}]


async def test_keeps_separate_slots_separate(client, db):
    doctors = await insert_doctors(
        db, [("Dr. Hart", "General Medicine"), ("Dr. Silva", "General Medicine")]
    )
    s1 = utc(10, 0)
    s2 = utc(10, 30)
    await insert_availability(db, doctors[0], s1)
    await insert_availability(db, doctors[1], s2)

    response = await client.get("/api/slots")
    body = sorted(response.json(), key=lambda s: s["startsAt"])
    assert body == [
        {"startsAt": iso(s1), "availableDoctors": 1},
        {"startsAt": iso(s2), "availableDoctors": 1},
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
                "startsAt": iso(slot),
                "availableDoctors": expected_available,
            }
        ]


async def test_slots_are_sorted_chronologically(client, db):
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    s1 = utc(16, 0)
    s2 = utc(10, 0)
    s3 = utc(12, 0)
    await insert_availability(db, doctors[0], s1)
    await insert_availability(db, doctors[0], s2)
    await insert_availability(db, doctors[0], s3)

    response = await client.get("/api/slots")
    starts = [s["startsAt"] for s in response.json()]
    assert starts == [iso(s2), iso(s3), iso(s1)]


async def test_past_slots_are_excluded(client, db):
    """Slots in the past should not appear in the listing."""
    doctors = await insert_doctors(db, [("Dr. Hart", "General Medicine")])
    past_slot = utc(10, 0, day_offset=-1)
    future_slot = utc(10, 0)
    await insert_availability(db, doctors[0], past_slot)
    await insert_availability(db, doctors[0], future_slot)

    response = await client.get("/api/slots")
    starts = [s["startsAt"] for s in response.json()]
    assert iso(past_slot) not in starts
    assert iso(future_slot) in starts
