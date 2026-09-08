import pytest
from datetime import time
from models.Event import Event
from models.Timeslot import TimeSlot
from services.scheduler_service import SchedulerService
from exceptions import EmptyPersonListError, InvalidDurationError, PersonNotFoundError
from tests.mock_repository import MockEventRepository


@pytest.fixture
def mock_repo():
    data = {
        "Alice": [
            Event(subject="Meeting", start=time(9, 0), end=time(10, 0)),
            Event(subject="Lunch", start=time(13, 0), end=time(14, 0)),
        ],
        "Bob": [
            Event(subject="Call", start=time(9, 30), end=time(10, 30)),
            Event(subject="Review", start=time(15, 0), end=time(16, 0)),
        ]
    }
    return MockEventRepository(data)


def test_find_common_free_slots_success(mock_repo):
    service = SchedulerService(event_repository=mock_repo, day_start=time(8, 0), day_end=time(18, 0))
    slots = service.find_common_free_slots(["Alice", "Bob"], duration_minutes=60)

    assert len(slots) == 4
    assert slots[0] == TimeSlot(start=time(8, 0), end=time(9, 0))
    assert slots[1] == TimeSlot(start=time(10, 30), end=time(13, 0))
    assert slots[2] == TimeSlot(start=time(14, 0), end=time(15, 0))
    assert slots[3] == TimeSlot(start=time(16, 0), end=time(18, 0))


def test_empty_participants_list_raises_error(mock_repo):
    service = SchedulerService(event_repository=mock_repo)
    with pytest.raises(EmptyPersonListError):
        service.find_common_free_slots([], duration_minutes=30)


def test_invalid_duration_raises_error(mock_repo):
    service = SchedulerService(event_repository=mock_repo)
    with pytest.raises(InvalidDurationError):
        service.find_common_free_slots(["Alice"], duration_minutes=0)


def test_person_not_found_raises_error(mock_repo):
    service = SchedulerService(event_repository=mock_repo)
    with pytest.raises(PersonNotFoundError):
        service.find_common_free_slots(["Alice", "Charlie"], duration_minutes=30)