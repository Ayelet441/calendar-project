from datetime import datetime, time, timedelta
from typing import List
from models.TimeSlot import TimeSlot
from repository.event_repository import EventRepository

class AvailabilityService:
    def __init__(self, event_repository: EventRepository):
        self.event_repository = event_repository

    def find_available_slots(self, person_list: List[str], event_duration: timedelta) -> List[TimeSlot]:
        day_start = time(7, 0)
        day_end = time(19, 0)

        all_events = []
        for person in person_list:
            events = self.event_repository.get_by_person(person)
            if events:
                all_events.extend(events)

        dummy_date = datetime.today().date()
        day_start_dt = datetime.combine(dummy_date, day_start)
        day_end_dt = datetime.combine(dummy_date, day_end)

        if not all_events:
            if day_end_dt - day_start_dt >= event_duration:
                return [Timeslot(start=day_start, end=day_end)]
            return []

        intervals = []
        for event in all_events:
            start_dt = datetime.combine(dummy_date, event.start)
            end_dt = datetime.combine(dummy_date, event.end)
            intervals.append((start_dt, end_dt))

        intervals.sort(key=lambda x: x[0])

        merged_intervals = []
        current_start, current_end = intervals[0]
        for next_start, next_end in intervals[1:]:
            if next_start <= current_end:
                if next_end > current_end:
                    current_end = next_end
            else:
                merged_intervals.append((current_start, current_end))
                current_start, current_end = next_start, next_end
        merged_intervals.append((current_start, current_end))

        available_slots = []
        last_end = day_start_dt

        for start_dt, end_dt in merged_intervals:
            if start_dt > last_end:
                gap_duration = start_dt - last_end
                if gap_duration >= event_duration:
                    available_slots.append(TimeSlot(start=last_end.time(), end=start_dt.time()))
            if end_dt > last_end:
                last_end = end_dt

        if last_end < day_end_dt:
            gap_duration = day_end_dt - last_end
            if gap_duration >= event_duration:
                available_slots.append(TimeSlot(start=last_end.time(), end=day_end_dt.time()))

        return available_slots