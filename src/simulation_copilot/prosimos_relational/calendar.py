import sqlalchemy as sa
import sqlalchemy.orm

from simulation_copilot.prosimos.resource_model import Day
from simulation_copilot.prosimos_relational.base import _Base


class CalendarInterval(_Base):
    """An interval in a calendar that defines the availability of a resource or the arrival of cases."""

    __tablename__ = "calendar_interval"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    start_day = sa.Column(sa.Enum(Day), nullable=False)
    """The start day of the interval, e.g. Monday, Tuesday, etc."""
    end_day = sa.Column(sa.Enum(Day), nullable=False)
    """The end day of the interval, e.g. Monday, Tuesday, etc."""
    start_time_hour = sa.Column(sa.Integer, nullable=False)
    """The start hour of the interval, e.g. 8 for 8:00 AM, 13 for 1:00 PM, etc."""
    start_time_minute = sa.Column(sa.Integer, nullable=False)
    """The start minute of the interval, e.g. 0 for 8:00 AM, 30 for 8:30 AM, etc."""
    end_time_hour = sa.Column(sa.Integer, nullable=False)
    """The end hour of the interval, e.g. 8 for 8:00 AM, 13 for 1:00 PM, etc."""
    end_time_minute = sa.Column(sa.Integer, nullable=False)
    """The end minute of the interval, e.g. 0 for 8:00 AM, 30 for 8:30 AM, etc."""
    calendar_id = sa.Column(sa.String, sa.ForeignKey("calendar.id"), nullable=False)
    """The calendar to which this interval belongs."""


class Calendar(_Base):
    """The calendar can define resource availability, case arrival times, and other time-based events."""

    __tablename__ = "calendar"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    intervals = sa.orm.relationship(CalendarInterval, backref="calendar")
    """The intervals that define the availability of resources or case arrival times."""
