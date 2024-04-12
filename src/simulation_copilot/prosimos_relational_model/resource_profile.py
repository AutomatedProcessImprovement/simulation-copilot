import sqlalchemy as sa
import sqlalchemy.orm

from simulation_copilot.prosimos_relational_model.base import _Base


class Activity(_Base):
    """Activity is a task that is performed by a resource."""

    __tablename__ = "activity"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    """The BPMN ID of the activity from the BPMN model."""
    name = sa.Column(sa.String, nullable=False)
    """The name of the activity."""
    resource_id = sa.Column(sa.Integer, sa.ForeignKey("resource.id"), nullable=False)
    """The resource that performs this activity."""


class ActivityResourceDistribution(_Base):
    """The activity distribution for the simulator."""

    __tablename__ = "activity_resource_distribution"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    activity_id = sa.Column(sa.Integer, sa.ForeignKey("activity.id"), nullable=False)
    """The activity to which this distribution belongs."""
    resource_id = sa.Column(sa.Integer, sa.ForeignKey("resource.id"), nullable=False)
    """The resource that performs this activity."""
    distribution_id = sa.Column(sa.Integer, sa.ForeignKey("distribution.id"), nullable=False)
    """The distribution of the duration of the activity."""


class Resource(_Base):
    """Resource is a person, machine, or other entity that performs activities."""

    __tablename__ = "resource"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    """The BPMN ID of the resource from the BPMN model."""
    name = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Integer, nullable=False)
    """The amount of this resource available in the simulation."""
    cost_per_hour = sa.Column(sa.Float, nullable=False)
    """The cost per hour of this resource."""
    calendar_id = sa.Column(sa.Integer, sa.ForeignKey("calendar.id"), nullable=False)
    """The calendar of availability for this resource."""
    profile_id = sa.Column(sa.Integer, sa.ForeignKey("resource_profile.id"), nullable=False)
    """The profile this resource belongs to."""
    assigned_activities = sa.orm.relationship(ActivityResourceDistribution, backref="resource")
    """The activities assigned to this resource and their distributions."""


class ResourceProfile(_Base):
    """Resource profile is a collection of resources."""

    __tablename__ = "resource_profile"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    """The name of the resource profile, e.g., full-time, part-time, senior, junior."""
    resources = sa.orm.relationship(Resource, backref="profile")
    """The resources in this profile."""
    simulation_model_id = sa.Column(sa.Integer, sa.ForeignKey("simulation_model.id"), nullable=False)
    """The simulation model this profile belongs to."""
