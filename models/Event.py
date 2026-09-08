from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class Event:
    """
    Represents a calendar event with a subject, start time, and end time.
    Immutable value object to prevent unintended modifications.
    """
    subject: str
    start: time
    end: time