import os
import logging
from datetime import datetime, date, timedelta
from repository.csv_event_repository import CsvEventRepository
from services.availability_service import AvailabilityService
from exceptions import CalendarError

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_calendar_app():
    # Define the path to the CSV file inside the resources folder
    csv_file_path = os.path.join(os.path.dirname(__file__), "..", "resources", "calendar.csv")

    try:
        # Initialize repository and availability service (working hours are handled inside the service)
        event_repo = CsvEventRepository(csv_file_path=csv_file_path)
        scheduler = AvailabilityService(event_repository=event_repo)

        # Get participants input from user
        participants_input = input("Enter meeting participants (comma-separated, e.g., Alice, Jack): ").strip()
        if not participants_input:
            print("No participants entered.")
            return

        participants = [p.strip() for p in participants_input.split(",") if p.strip()]

        # Get duration input from user
        duration_input = input(
            "Enter meeting duration in minutes (e.g., 60 for an hour, 30 for half an hour): ").strip()
        try:
            duration_minutes = int(duration_input)
        except ValueError:
            print("Duration must be a whole number of minutes.")
            return

        duration = timedelta(minutes=duration_minutes)

        # Search for available time slots
        print(f"\nSearching for free slots for {participants} for a {duration_minutes}-minute meeting...\n")
        available_slots = scheduler.find_available_slots(participants, duration=duration)

        if not available_slots:
            print("No common free slots found for the selected participants.")
            return

        # Display results in the requested format
        print("Available Time Slots Found:")
        for slot in available_slots:
            start_str = slot.start.strftime("%H:%M")
            slot_end_dt = datetime.combine(date.min, slot.end)
            latest_start_dt = slot_end_dt - duration
            latest_start_str = latest_start_dt.time().strftime("%H:%M")

            if slot.start == latest_start_dt.time():
                print(f"Starting Time of available slots: {start_str}")
            else:
                print(f"Starting Time of available slots: {start_str} - {latest_start_str}")

    except CalendarError as e:
        print(f"\n[Error] {e}")
    except Exception as e:
        print(f"\n[Critical Error] {e}")


if __name__ == "__main__":
    run_calendar_app()