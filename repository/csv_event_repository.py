import csv
from datetime import datetime
from typing import List

from models.Event import Event
from repository.event_repository import EventRepository


class CsvEventRepository(EventRepository):

    def __init__(self, csv_file_path: str):
        self.csv_file_path = csv_file_path

    def get_by_person(self, person_name: str) -> List[Event]:
        events = []

        with open(self.csv_file_path, newline="", encoding="utf-8") as csv_file:
            reader = csv.reader(csv_file)

            for row in reader:
                if row[0] != person_name:
                    continue

                start = datetime.strptime(
                    row[2],
                    "%H:%M"
                ).time()

                end = datetime.strptime(
                    row[3],
                    "%H:%M"
                ).time()

                events.append(
                    Event(
                        subject=row[1],
                        start=start,
                        end=end,
                    )
                )

        return events
