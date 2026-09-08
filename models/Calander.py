from dataclasses import dataclass, field
from typing import Dict
from .Person import Person


@dataclass
class Calendar:
    """
    Represents the main calendar containing all registered people and managed data.
    Mutable container entity.
    """
    people: Dict[str, Person] = field(default_factory=dict)

    def add_person(self, person: Person) -> None:
        """
        Adds a new person to the calendar dictionary.

        Args:
            person (Person): The person object to add.
        """
        self.people[person.name] = person

    def get_person(self, name: str) -> Person:
        """
        Retrieves a Person object by their name.

        Args:
            name (str): The name of the person.

        Returns:
            Person: The corresponding Person object.
        """
        return self.people[name]

    def has_person(self, name: str) -> bool:
        """
        Checks whether a person exists in the calendar.

        Args:
            name (str): The name of the person to check.

        Returns:
            bool: True if the person exists, False otherwise.
        """
        return name in self.people