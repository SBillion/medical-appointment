from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Appointment, DoctorAvailability


class AppointmentRepository:
    """Creates and reads appointment records."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create(self, availability: DoctorAvailability) -> Appointment:
        appointment = Appointment(doctor_availability_id=availability.id)
        self._db.add(appointment)
        return appointment
