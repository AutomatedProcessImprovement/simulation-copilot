import sqlalchemy as sa

from simulation_copilot.prosimos_relational import Base


class Activity(Base):
    __tablename__ = "activities"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    resource_id = sa.Column(sa.String, sa.ForeignKey("resources.id"), nullable=False)


class ActivityDistribution(Base):
    __tablename__ = "activity_distributions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    resource_id = sa.Column(sa.String, sa.ForeignKey("resources.id"), nullable=False)
    activity_id = sa.Column(sa.String, sa.ForeignKey("activities.id"), nullable=False)
    distribution_id = sa.Column(sa.String, sa.ForeignKey("distributions.id"), nullable=False)


class Resource(Base):
    __tablename__ = "resources"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    name = sa.Column(sa.String, nullable=False)
    amount = sa.Column(sa.Integer, nullable=False)
    cost_per_hour = sa.Column(sa.Float, nullable=False)
    calendar_id = sa.Column(sa.String, sa.ForeignKey("calendars.id"), nullable=False)
    profile_id = sa.Column(sa.String, sa.ForeignKey("resource_profiles.id"), nullable=False)
    assigned_activities = sa.orm.relationship("ActivityDistribution", backref="resource")


class ResourceProfile(Base):
    __tablename__ = "resource_profiles"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    resources = sa.orm.relationship("Resource", backref="profile")
    simulation_model_id = sa.Column(sa.String, sa.ForeignKey("simulation_models.id"), nullable=False)
