from dataclasses import dataclass, field
from typing import List
from .Event import Event


@dataclass
class Person:
    """
    Represents a person holding a list of associated events in the calendar.
    Mutable entity to allow adding events dynamically.
    """
    name: str
    events: List[Event] = field(default_factory=list)

    def add_event(self, event: Event) -> None:
        """
        Adds a new event to the person's event list.

        Args:
            event (Event): The event object to add.
        """
        self.events.append(event)