from datetime import timedelta
from repository.csv_event_repository import CsvEventRepository
from services.availability_service import AvailabilityService
from datetime import datetime, date

repo = CsvEventRepository("../resources/calendar.csv")
availability_service = AvailabilityService(repo)

people = ["Alice", "Jack"]
duration = timedelta(minutes=60)

available_slots = availability_service.find_available_slots(people, duration)
for slot in available_slots:
    start_str = slot.start.strftime("%H:%M")


    slot_end_dt = datetime.combine(date.min, slot.end)
    latest_start_dt = slot_end_dt - duration
    latest_start_str = latest_start_dt.time().strftime("%H:%M")

    if slot.start == latest_start_dt.time():
        print(f"Starting Time of available slots: {start_str}")
    else:
        print(f"Starting Time of available slots: {start_str} - {latest_start_str}")