from enum import Enum
from uuid import uuid4

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool


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
    resources: list[Resource]


class ResourceModel(BaseModel):
    """
    ResourceModel is the class that represents resources of the business process
    simulation model.

    It includes resource profiles, resource calendars, and distribution of activities
    among the given resources.
    """

    profiles: list[ResourceProfile]
    calendars: list[Calendar]


example_model = ResourceModel(
    profiles=[
        ResourceProfile(
            id="profile_1",
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


class IntervalDescriptionInput(BaseModel):
    start_day: str = Field(description="The day of the week when the calendar starts")
    end_day: str = Field(description="The day of the week when the calendar ends")
    start_time: str = Field(
        description="The time when the calendar starts in ISO format (HH:MM) where HH is the hour in 24-hour format and MM is the minute, 0-59."
    )
    end_time: str = Field(
        description="The time when the calendar ends  in ISO format (HH:MM) where HH is the hour in 24-hour format and MM is the minute, 0-59."
    )


class GenerateCalendarInput(BaseModel):
    intervals: list[IntervalDescriptionInput] = Field(
        description="The intervals of the calendar"
    )


@tool("generate_calendar", args_schema=GenerateCalendarInput)
def generate_calendar(
    intervals: list[IntervalDescriptionInput],
) -> Calendar:
    """
    Generate a calendar with the given intervals. Put distinct intervals in separate
    calendar intervals.
    """
    return Calendar(
        id=uuid4().hex,
        intervals=[
            CalendarInterval(
                start_day=Day.from_string(interval.start_day),
                end_day=Day.from_string(interval.end_day),
                start_time=Time.from_iso_time(interval.start_time),
                end_time=Time.from_iso_time(interval.end_time),
            )
            for interval in intervals
        ],
    )


class ActivityDistributionInput(BaseModel):
    activity_id: str = Field(description="The id of the activity")
    distribution: Distribution = Field(
        description="The distribution of the activity in the form of a name of the distribution and a list of parameters specific to the distribution"
    )


class ResourceInput(BaseModel):
    resource_name: str = Field(description="The name of the resource")
    amount: int = Field(description="The amount of the resource")
    cost_per_hour: float = Field(description="The cost per hour of the resource")
    calendar_id: str = Field(description="The id of the calendar")
    activities: list[ActivityDistributionInput] = Field(
        description="The distribution of the activity in the form of a name of the distribution and a list of parameters specific to the distribution"
    )


class GenerateResourceProfileInput(BaseModel):
    resources: list[ResourceInput] = Field(
        description="The resources with their assigned activities"
    )


@tool("generate_resource_profile", args_schema=GenerateResourceProfileInput)
def generate_resource_profile(
    resources: list[ResourceInput],
) -> ResourceProfile:
    """
    Generate a resource profile with the given resources and their assigned activities.
    """
    return ResourceProfile(
        id=uuid4().hex,
        resources=[
            Resource(
                id=uuid4().hex,
                name=resource.resource_name,
                amount=resource.amount,
                cost_per_hour=resource.cost_per_hour,
                calendar_id=resource.calendar_id,
                assigned_activities=[
                    ActivityDistribution(
                        activity_id=activity.activity_id,
                        distribution=activity.distribution,
                    )
                    for activity in resource.activities
                ],
            )
            for resource in resources
        ],
    )
