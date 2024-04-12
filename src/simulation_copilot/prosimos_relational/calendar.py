import sqlalchemy as sa

from simulation_copilot.prosimos.resource_model import Day
from simulation_copilot.prosimos_relational.base import _Base


class CalendarInterval(_Base):
    __tablename__ = "calendar_intervals"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    start_day = sa.Column(sa.Enum(Day), nullable=False)
    end_day = sa.Column(sa.Enum(Day), nullable=False)
    start_time_hour = sa.Column(sa.Integer, nullable=False)
    start_time_minute = sa.Column(sa.Integer, nullable=False)
    end_time_hour = sa.Column(sa.Integer, nullable=False)
    end_time_minute = sa.Column(sa.Integer, nullable=False)
    calendar_id = sa.Column(sa.String, sa.ForeignKey("calendars.id"), nullable=False)


class Calendar(_Base):
    __tablename__ = "calendars"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    intervals = sa.orm.relationship("CalendarInterval", backref="calendar")
