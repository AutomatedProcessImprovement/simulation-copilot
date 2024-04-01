from uuid import uuid4

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from simulation_copilot.lib.resource_model import Calendar, CalendarInterval, Day, Time


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
def generate_calendar(intervals: list[IntervalDescriptionInput]) -> Calendar:
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
