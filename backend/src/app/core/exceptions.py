"""Domain-level exceptions shared across layers."""


class SlotUnavailableError(Exception):
    """No doctor availability matches the requested start time."""


class SlotAlreadyBookedError(Exception):
    """All candidate availabilities for the slot are already booked."""


__all__ = [
    "SlotUnavailableError",
    "SlotAlreadyBookedError",
]
