import heapq
import logging
from datetime import datetime, time, timedelta
from typing import List, Protocol
from models.Event import Event
from models.TimeSlot import TimeSlot
from exceptions import (
    EmptyPersonListError,
    InvalidDurationError,
    PersonNotFoundError,
)

logger = logging.getLogger(__name__)


class EventRepositoryProtocol(Protocol):
    def get_by_person(self, person_name: str) -> List[Event]:
        ...


class AvailabilityService:
    """
    Service responsible for finding full available time gaps for multiple participants.
    Working hours are strictly defined internally.
    """

    def __init__(self, event_repository: EventRepositoryProtocol):
        self.event_repository = event_repository
        # Working hours defined exclusively within the service
        self.day_start = time(7, 0)
        self.day_end = time(19, 0)

    def find_available_slots(
            self,
            participants: List[str],
            duration: timedelta
    ) -> List[TimeSlot]:
        # Early escape: validate inputs immediately before executing any heavy logic
        if not participants:
            logger.warning("Attempted to find slots with an empty participant list.")
            raise EmptyPersonListError("Participant list cannot be empty.")

        duration_minutes = int(duration.total_seconds() / 60)
        if duration_minutes <= 0:
            logger.warning("Invalid meeting duration requested: %d minutes.", duration_minutes)
            raise InvalidDurationError("Meeting duration must be greater than zero.")

        # Step 1: Collect and sort events for all participants into minute intervals
        participant_lists = []
        for person_name in participants:
            events = self.event_repository.get_by_person(person_name)
            intervals = [(e.start.hour * 60 + e.start.minute, e.end.hour * 60 + e.end.minute) for e in events]
            intervals.sort(key=lambda x: x[0])
            participant_lists.append(intervals)

        # Step 2: Merge intervals using Two-Pointer for 2 participants or Min-Heap for K participants
        if len(participants) == 2:
            logger.info("Using O(n+m) Two-Pointer merge for 2 participants: %s", participants)
            merged_busy = self._merge_two_lists(participant_lists[0], participant_lists[1])
        else:
            logger.info("Using O(N log K) Min-Heap merge for %d participants: %s", len(participants), participants)
            merged_busy = self._merge_multiple_lists(participant_lists)

        # Step 3: Scan the merged timeline to find full available gaps >= duration
        work_start_mins = self.day_start.hour * 60 + self.day_start.minute
        work_end_mins = self.day_end.hour * 60 + self.day_end.minute
        available_slots: List[TimeSlot] = []
        current_time = work_start_mins

        for start, end in merged_busy:
            if current_time < start:
                if start - current_time >= duration_minutes:
                    slot_start = (datetime.min + timedelta(minutes=current_time)).time()
                    slot_end = (datetime.min + timedelta(minutes=start)).time()
                    available_slots.append(TimeSlot(start=slot_start, end=slot_end))
            current_time = max(current_time, end)

        if work_end_mins - current_time >= duration_minutes:
            slot_start = (datetime.min + timedelta(minutes=current_time)).time()
            slot_end = (datetime.min + timedelta(minutes=work_end_mins)).time()
            available_slots.append(TimeSlot(start=slot_start, end=slot_end))

        logger.info("Search completed. Found %d available slots in total.", len(available_slots))
        return available_slots

    def _merge_two_lists(self, list1: List[tuple], list2: List[tuple]) -> List[tuple]:
        p1, p2 = 0, 0
        merged_busy = []

        while p1 < len(list1) and p2 < len(list2):
            if list1[p1][0] <= list2[p2][0]:
                current_interval = list1[p1]
                p1 += 1
            else:
                current_interval = list2[p2]
                p2 += 1

            if merged_busy and merged_busy[-1][1] >= current_interval[0]:
                merged_busy[-1] = (merged_busy[-1][0], max(merged_busy[-1][1], current_interval[1]))
            else:
                merged_busy.append(current_interval)

        for lst, p in [(list1, p1), (list2, p2)]:
            while p < len(lst):
                curr = lst[p]
                p += 1
                if merged_busy and merged_busy[-1][1] >= curr[0]:
                    merged_busy[-1] = (merged_busy[-1][0], max(merged_busy[-1][1], curr[1]))
                else:
                    merged_busy.append(curr)

        return merged_busy

    def _merge_multiple_lists(self, participant_lists: List[List[tuple]]) -> List[tuple]:
        min_heap = []
        for p_idx, intervals in enumerate(participant_lists):
            if intervals:
                heapq.heappush(min_heap, (intervals[0][0], intervals[0][1], p_idx, 0))

        merged_busy = []
        while min_heap:
            start, end, p_idx, i_idx = heapq.heappop(min_heap)

            if merged_busy and merged_busy[-1][1] >= start:
                merged_busy[-1] = (merged_busy[-1][0], max(merged_busy[-1][1], end))
            else:
                merged_busy.append((start, end))

            next_i_idx = i_idx + 1
            if next_i_idx < len(participant_lists[p_idx]):
                next_interval = participant_lists[p_idx][next_i_idx]
                heapq.heappush(min_heap, (next_interval[0], next_interval[1], p_idx, next_i_idx))

        return merged_busy