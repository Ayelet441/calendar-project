from typing import List, Protocol
from models.Event import Event


class EventRepository(Protocol):
    """
    Protocol defining the interface for event data retrieval.
    Allows structural subtyping for flexible implementations and unit testing.
    """

    def get_by_person(self, person_name: str) -> List[Event]:
        """
        Retrieves a list of events associated with a specific person.

        Args:
            person_name (str): The name of the person.

        Returns:
            List[Event]: A list of Event objects.
        """
        ...