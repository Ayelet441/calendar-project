import pytest
from datetime import time, timedelta
from models.Event import Event
from models.Timeslot import TimeSlot
from services.availability_service import AvailabilityService
from exceptions import (
    EmptyPersonListError,
    InvalidDurationError,
    PersonNotFoundError,
)
from tests.mock_repository import MockEventRepository


@pytest.fixture
def mock_repo():
    """
    Fixture providing sample data for testing AvailabilityService.
    """
    data = {
        "Alice": [
            Event(subject="Morning meeting", start=time(8, 0), end=time(9, 30)),
            Event(subject="Lunch with Jack", start=time(13, 0), end=time(14, 0)),
            Event(subject="Yoga", start=time(16, 0), end=time(17, 0)),
        ],
        "Jack": [
            Event(subject="Morning meeting", start=time(8, 0), end=time(8, 50)),
            Event(subject="Sales call", start=time(9, 0), end=time(9, 40)),
            Event(subject="Lunch with Alice", start=time(13, 0), end=time(14, 0)),
            Event(subject="Yoga", start=time(16, 0), end=time(17, 0)),
        ],
        "BusyPerson": [
            # A person who is busy the entire working day (07:00 to 18:00)
            Event(subject="All-day shift", start=time(7, 0), end=time(18, 0)),
        ]
    }
    return MockEventRepository(data)


def test_find_available_slots_two_participants(mock_repo):
    """
    Test finding common free slots for 2 participants using Two-Pointer merge.
    """
    service = AvailabilityService(event_repository=mock_repo)
    slots = service.find_available_slots(["Alice", "Jack"], duration=timedelta(minutes=60))

    assert len(slots) == 4
    assert slots[0] == TimeSlot(start=time(7, 0), end=time(8, 0))
    assert slots[1] == TimeSlot(start=time(9, 40), end=time(13, 0))
    assert slots[2] == TimeSlot(start=time(14, 0), end=time(15, 0))
    assert slots[3] == TimeSlot(start=time(17, 0), end=time(18, 0))


def test_find_available_slots_single_participant(mock_repo):
    """
    Test finding available slots for a single participant.
    """
    service = AvailabilityService(event_repository=mock_repo)
    slots = service.find_available_slots(["Alice"], duration=timedelta(minutes=60))

    # Alice has gaps: 07:00-08:00, 09:30-13:00, 14:00-16:00, 17:00-18:00
    assert len(slots) == 4
    assert slots[0] == TimeSlot(start=time(7, 0), end=time(8, 0))
    assert slots[1] == TimeSlot(start=time(9, 30), end=time(13, 0))


def test_empty_participants_list_raises_error(mock_repo):
    """
    Edge case: Passing an empty list of participants should raise EmptyPersonListError.
    """
    service = AvailabilityService(event_repository=mock_repo)
    with pytest.raises(EmptyPersonListError):
        service.find_available_slots([], duration=timedelta(minutes=30))


def test_zero_duration_raises_error(mock_repo):
    """
    Edge case: Passing a zero duration should raise InvalidDurationError.
    """
    service = AvailabilityService(event_repository=mock_repo)
    with pytest.raises(InvalidDurationError):
        service.find_available_slots(["Alice"], duration=timedelta(minutes=0))


def test_negative_duration_raises_error(mock_repo):
    """
    Edge case: Passing a negative duration should raise InvalidDurationError.
    """
    service = AvailabilityService(event_repository=mock_repo)
    with pytest.raises(InvalidDurationError):
        service.find_available_slots(["Alice"], duration=timedelta(minutes=-15))


def test_person_not_found_raises_error(mock_repo):
    """
    Edge case: Requesting a person who does not exist in the repository should raise PersonNotFoundError.
    """
    service = AvailabilityService(event_repository=mock_repo)
    with pytest.raises(PersonNotFoundError):
        service.find_available_slots(["Alice", "NonExistentPerson"], duration=timedelta(minutes=30))


def test_no_available_slots_due_to_full_schedule(mock_repo):
    """
    Edge case: When participants are completely busy, no slots should be returned.
    """
    service = AvailabilityService(event_repository=mock_repo)
    # BusyPerson is booked from 07:00 to 18:00
    slots = service.find_available_slots(["BusyPerson"], duration=timedelta(minutes=60))

    assert len(slots) == 0


def test_duration_larger_than_any_gap(mock_repo):
    """
    Edge case: Requesting a meeting duration longer than any available gap should return no slots.
    """
    service = AvailabilityService(event_repository=mock_repo)
    # The largest gap between Alice and Jack is 09:40 to 13:00 (3 hours and 20 mins).
    # Requesting 4 hours (240 mins) should yield no results.
    slots = service.find_available_slots(["Alice", "Jack"], duration=timedelta(hours=4))

    assert len(slots) == 0