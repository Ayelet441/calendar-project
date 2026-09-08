import csv
import logging
from datetime import datetime
from typing import List

from models.Event import Event
from exceptions import CalendarDataError, PersonNotFoundError

logger = logging.getLogger(__name__)


class CsvEventRepository:
    """
    CSV file-based implementation of the EventRepository protocol.
    """

    def __init__(self, csv_file_path: str):
        """
        Initializes the CSV repository with the target file path.

        Args:
            csv_file_path (str): The path to the calendar CSV file.
        """
        self.csv_file_path = csv_file_path

    def get_by_person(self, person_name: str) -> List[Event]:
        """
        Reads the CSV file and retrieves all events for the specified person.

        Args:
            person_name (str): The name of the person to filter by.

        Returns:
            List[Event]: A list of parsed Event objects.

        Raises:
            CalendarDataError: If the file is missing or parsing fails.
            PersonNotFoundError: If the person does not exist in the calendar data source.
        """
        events = []
        person_exists = False
        logger.info("Loading events for person '%s' from CSV: %s", person_name, self.csv_file_path)

        try:
            with open(self.csv_file_path, newline="", encoding="utf-8") as csv_file:
                reader = csv.reader(csv_file)

                for row_idx, row in enumerate(reader, start=1):
                    if not row or len(row) < 4:
                        continue  # Skip empty or malformed rows

                    current_person = row[0].strip()

                    # Track if the person exists anywhere in the file
                    if current_person == person_name:
                        person_exists = True

                    if current_person != person_name:
                        continue

                    try:
                        start = datetime.strptime(
                            row[2].strip(),
                            "%H:%M"
                        ).time()

                        end = datetime.strptime(
                            row[3].strip(),
                            "%H:%M"
                        ).time()

                        # Validate time range consistency
                        if start >= end:
                            raise CalendarDataError(f"Start time must be before end time at row {row_idx}.")

                        events.append(
                            Event(
                                subject=row[1].strip(),
                                start=start,
                                end=end,
                            )
                        )
                    except (ValueError, IndexError) as e:
                        if isinstance(e, CalendarDataError):
                            raise
                        logger.error("Failed to parse row %d in CSV file: %s", row_idx, e)
                        raise CalendarDataError(f"Invalid data format at row {row_idx}: {e}") from e

        except FileNotFoundError as e:
            logger.error("Calendar CSV file not found at path: %s", self.csv_file_path)
            raise CalendarDataError(f"Calendar file not found: {self.csv_file_path}") from e
        except Exception as e:
            if isinstance(e, (CalendarDataError, PersonNotFoundError)):
                raise
            logger.error("Unexpected error occurred while reading CSV: %s", e)
            raise CalendarDataError(f"Unexpected error reading calendar data: {e}") from e

        # If the person was queried but never found in the data source, raise explicit error
        if not person_exists:
            logger.warning("Person '%s' was not found in the calendar records.", person_name)
            raise PersonNotFoundError(f"Person '{person_name}' does not exist in the system.")

        logger.info("Successfully loaded %d events for '%s'", len(events), person_name)
        return events