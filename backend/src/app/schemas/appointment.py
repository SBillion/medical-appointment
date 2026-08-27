from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field, field_serializer
from pydantic.alias_generators import to_camel


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


def _utc_iso(dt: datetime) -> str:
    return _ensure_utc(dt).strftime("%Y-%m-%dT%H:%M:%SZ")


class AppointmentSlotOut(BaseModel):
    """An available slot aggregated by start time across all doctors."""

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    starts_at: datetime
    available_doctors: int = Field(ge=0)

    @field_serializer("starts_at")
    def _serialize_starts_at(self, value: datetime) -> str:
        return _utc_iso(value)


class BookingRequest(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    starts_at: datetime


class DoctorOut(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,
    )

    id: int
    full_name: str
    specialty: str


class BookingOut(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )

    id: int
    starts_at: datetime
    ends_at: datetime
    doctor: DoctorOut

    @field_serializer("starts_at", "ends_at")
    def _serialize_dt(self, value: datetime) -> str:
        return _utc_iso(value)


class ErrorOut(BaseModel):
    detail: str
