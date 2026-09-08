from models.Event import Event
from exceptions import PersonNotFoundError


class MockEventRepository:
    """
    Mock repository for testing SchedulerService without file system dependencies.
    Lives entirely in memory during test execution.
    """
    def __init__(self, data_map):
        self.data_map = data_map

    def get_by_person(self, person_name: str) -> list[Event]:
        if person_name not in self.data_map:
            raise PersonNotFoundError(f"Person '{person_name}' does not exist.")
        return self.data_map[person_name]