import sqlalchemy as sa

from simulation_copilot.prosimos_relational.base import _Base


class SimulationModel(_Base):
    __tablename__ = "simulation_models"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    resource_profiles = sa.orm.relationship("ResourceProfile", backref="simulation_model")
    """Resource profiles with resources and their assigned activities."""
    gateways = sa.orm.relationship("Gateway", backref="simulation_model")
    """Gateways, their probabilities and sequence flows."""
    case_arrival = sa.orm.relationship("CaseArrival", backref="simulation_model")
    """The calendar of case arrivals and distribution of inter-arrival times."""
