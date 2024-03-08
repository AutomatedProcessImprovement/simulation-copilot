import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from simulation_copilot.resource_model import Day

Base = declarative_base()


class CalendarInterval(Base):
    __tablename__ = "calendar_intervals"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    start_day = sa.Column(sa.Enum(Day), nullable=False)
    end_day = sa.Column(sa.Enum(Day), nullable=False)
    start_time_hour = sa.Column(sa.Integer, nullable=False)
    start_time_minute = sa.Column(sa.Integer, nullable=False)
    end_time_hour = sa.Column(sa.Integer, nullable=False)
    end_time_minute = sa.Column(sa.Integer, nullable=False)
    calendar_id = sa.Column(
        sa.String, sa.ForeignKey("calendars.id"), nullable=False
    )


class Calendar(Base):
    __tablename__ = "calendars"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    intervals = sa.orm.relationship("CalendarInterval", backref="calendar")


class Activity(Base):
    __tablename__ = "activities"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    resource_id = sa.Column(
        sa.String, sa.ForeignKey("resources.id"), nullable=False
    )


class DistributionParameters(Base):
    __tablename__ = "distribution_parameters"
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    activity_distribution_id = sa.Column(
        sa.String, sa.ForeignKey("activity_distributions.id"), nullable=False
    )
    parameter_name = sa.Column(sa.String, nullable=False)
    parameter_value = sa.Column(sa.Float, nullable=False)


class ActivityDistribution(Base):
    __tablename__ = "activity_distributions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    resource_id = sa.Column(
        sa.String, sa.ForeignKey("resources.id"), nullable=False
    )
    activity_id = sa.Column(
        sa.String, sa.ForeignKey("activities.id"), nullable=False
    )
    distribution_name = sa.Column(sa.String, nullable=False)
    distribution_parameters = sa.orm.relationship(
        "DistributionParameters", backref="activity_distribution"
    )


class Resource(Base):
    __tablename__ = "resources"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Integer, nullable=False)
    cost_per_hour = sa.Column(sa.Float, nullable=False)
    calendar_id = sa.Column(
        sa.String, sa.ForeignKey("calendars.id"), nullable=False
    )
    profile_id = sa.Column(
        sa.String, sa.ForeignKey("resource_profiles.id"), nullable=False
    )
    assigned_activities = sa.orm.relationship(
        "ActivityDistribution", backref="resource"
    )


class ResourceProfile(Base):
    __tablename__ = "resource_profiles"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    resources = sa.orm.relationship("Resource", backref="profile")
