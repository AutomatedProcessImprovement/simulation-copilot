import sqlalchemy as sa

from simulation_copilot.prosimos_relational import Base


class Distribution(Base):
    __tablename__ = "distributions"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    distribution_name = sa.Column(sa.String, nullable=False)
    distribution_parameters = sa.orm.relationship("DistributionParameters", backref="distribution")


class DistributionParameters(Base):
    __tablename__ = "distribution_parameters"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    distribution_id = sa.Column(sa.String, sa.ForeignKey("distributions.id"), nullable=False)
    parameter_name = sa.Column(sa.String, nullable=False)
    parameter_value = sa.Column(sa.Float, nullable=False)
