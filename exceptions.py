class CalendarError(Exception):
    """Base exception for all calendar application errors."""
    pass


class CalendarDataError(CalendarError):
    """Raised when an error occurs while loading or parsing calendar data."""
    pass


class PersonNotFoundError(CalendarError):
    """Raised when a requested person does not exist in the system or calendar."""
    pass


class InvalidTimeSlotError(CalendarError):
    """Raised when a time slot or event timeframe is invalid."""
    pass


class InvalidTimeRangeError(CalendarError):
    """Raised when an event's start time is after its end time or out of bounds."""
    pass


class EmptyPersonListError(CalendarError):
    """Raised when the participant list provided for slot searching is empty."""
    pass


class InvalidDurationError(CalendarError):
    """Raised when the requested meeting duration is invalid (zero, negative, or too long)."""
    pass