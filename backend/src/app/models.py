from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(Text, nullable=False)
    specialty: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    availabilities: Mapped[list["DoctorAvailability"]] = relationship(
        back_populates="doctor"
    )


class DoctorAvailability(Base):
    __tablename__ = "doctor_availabilities"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    doctor_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("doctors.id", ondelete="CASCADE"),
        nullable=False,
    )
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    doctor: Mapped[Doctor] = relationship(back_populates="availabilities")
    appointment: Mapped["Appointment | None"] = relationship(
        back_populates="availability", uselist=False
    )


class Appointment(Base):
    __tablename__ = "appointments"
    __table_args__ = (
        UniqueConstraint("doctor_availability_id", name="uq_appointment_availability"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    doctor_availability_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("doctor_availabilities.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    availability: Mapped[DoctorAvailability] = relationship(
        back_populates="appointment"
    )
