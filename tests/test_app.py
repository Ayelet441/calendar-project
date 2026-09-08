from datetime import timedelta

from repository.csv_event_repository import CsvEventRepository
from services.availability_service import AvailabilityService


def test_find_available_slots_alice_and_jack():
    repo = CsvEventRepository("io_comp/resources/calendar.csv")
    service = AvailabilityService(repo)

    people = ["Alice", "Jack"]
    duration = timedelta(minutes=60)

    slots = service.find_available_slots(people, duration)

    assert isinstance(slots, list)
    assert len(slots) > 0

    assert len(slots) == 4