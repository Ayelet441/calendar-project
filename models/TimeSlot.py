from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class TimeSlot:
    """
    Represents an available time slot within a day (start and end time range).
    Immutable value object to ensure data consistency.
    """
    start: time
    end: time