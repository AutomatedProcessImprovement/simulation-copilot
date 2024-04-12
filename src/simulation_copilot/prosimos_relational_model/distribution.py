import sqlalchemy as sa

from simulation_copilot.prosimos_relational_model.base import _Base


class DistributionParameter(_Base):
    __tablename__ = "distribution_parameter"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    distribution_id = sa.Column(sa.Integer, sa.ForeignKey("distribution.id"), nullable=False)
    """The distribution to which this parameter belongs."""
    name = sa.Column(sa.String, nullable=False)
    """The name of the parameter, e.g. "mean" or "stddev"."""
    value = sa.Column(sa.Float, nullable=False)
    """The value of the parameter."""


class Distribution(_Base):
    __tablename__ = "distribution"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    """The name of the distribution, e.g. "normal" or "exponential"."""
    parameters = sa.orm.relationship(DistributionParameter, backref="distribution", cascade="all, delete-orphan")
    """The parameters of the distribution."""
