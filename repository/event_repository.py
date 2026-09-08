from abc import ABC, abstractmethod
from typing import List

from models.Event import Event

class EventRepository(ABC):

    @abstractmethod
    def get_by_person(self, person_name: str) -> List[Event]:
        pass