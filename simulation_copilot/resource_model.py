from enum import Enum
from uuid import uuid4

from langchain.pydantic_v1 import BaseModel


class Day(str, Enum):
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"

    @staticmethod
    def from_iso_day(iso_day: int) -> "Day":
        return {
            1: Day.MONDAY,
            2: Day.TUESDAY,
            3: Day.WEDNESDAY,
            4: Day.THURSDAY,
            5: Day.FRIDAY,
            6: Day.SATURDAY,
            7: Day.SUNDAY,
        }[iso_day]

    @staticmethod
    def from_string(day: str) -> "Day":
        return {
            "monday": Day.MONDAY,
            "tuesday": Day.TUESDAY,
            "wednesday": Day.WEDNESDAY,
            "thursday": Day.THURSDAY,
            "friday": Day.FRIDAY,
            "saturday": Day.SATURDAY,
            "sunday": Day.SUNDAY,
        }[day.lower()]


class Time(BaseModel):
    hour: int  # 24-hour format
    minute: int  # 0-59

    @staticmethod
    def from_iso_time(iso_time: str) -> "Time":
        """
        Create a Time object from a string in ISO format (HH:MM). Where HH is the hour
        in 24-hour format and MM is the minute, 0-59.
        """
        hour, minute = map(int, iso_time.split(":"))
        return Time(hour=hour, minute=minute)


class CalendarInterval(BaseModel):
    start_day: Day
    end_day: Day
    start_time: Time
    end_time: Time

    def __post_init__(self):
        if not self.is_valid():
            raise ValueError("Invalid calendar interval")

    def is_valid(self):
        """
        The valid interval is when the start day is less than or equal to the end day.
        """
        return (
            self.start_day.value <= self.end_day.value
            and self.start_time.hour < self.end_time.hour
        )


class Calendar(BaseModel):
    id: str
    intervals: list[CalendarInterval]

    def merge(self, other: "Calendar") -> "Calendar":
        """
        Merge two calendars by combining their intervals.
        """
        # TODO: implement avoiding overlapping intervals
        return Calendar(id=uuid4().hex, intervals=self.intervals + other.intervals)


class Distribution(BaseModel):
    name: str
    parameters: list[float]


class ResourceDistribution(BaseModel):
    resource_id: str
    distribution: Distribution


class ActivityResourceDistribution(BaseModel):
    activity_id: str
    resource_distributions: list[ResourceDistribution]


class ActivityDistribution(BaseModel):
    activity_id: str
    distribution: Distribution


class Resource(BaseModel):
    id: str
    name: str
    amount: int
    cost_per_hour: float
    calendar_id: str
    assigned_activities: list[ActivityDistribution]


class ResourceProfile(BaseModel):
    id: str
    name: str
    resources: list[Resource]


class ResourceModel(BaseModel):
    """
    ResourceModel is the class that represents resources of the business process
    simulation model.

    It includes resource profiles, resource calendars, and distribution of activities
    among the given resources.

    example_model = ResourceModel(
        profiles=[
            ResourceProfile(
                id="profile_1",
                name="Profile 1",
                resources=[
                    Resource(
                        id="resource_1",
                        name="Resource 1",
                        amount=5,
                        cost_per_hour=10.0,
                        calendar_id="calendar_1",
                        assigned_activities=[
                            ActivityDistribution(
                                activity_id="activity_1",
                                distribution=Distribution(
                                    name="normal", parameters=[10, 2]
                                ),
                            )
                        ],
                    )
                ],
            )
        ],
        calendars=[
            Calendar(
                id="calendar_1",
                intervals=[
                    CalendarInterval(
                        start_day=Day.MONDAY,
                        end_day=Day.FRIDAY,
                        start_time=Time(hour=8, minute=0),
                        end_time=Time(hour=17, minute=0),
                    )
                ],
            )
        ],
    )
    """

    profiles: list[ResourceProfile]
    calendars: list[Calendar]

