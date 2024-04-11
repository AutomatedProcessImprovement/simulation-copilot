import sqlalchemy as sa

from simulation_copilot.prosimos_relational import Base


class SimulationModel(Base):
    __tablename__ = "simulation_models"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    resource_profiles = sa.orm.relationship("ResourceProfile", backref="simulation_model")
    """Resource profiles with resources and their assigned activities."""
    gateways = sa.orm.relationship("Gateway", backref="simulation_model")
    """Gateways, their probabilities and sequence flows."""
    case_arrival_id = sa.Column(sa.String, sa.ForeignKey("case_arrivals.id"), nullable=False)
    """Case arrival model which includes the calendar and inter-arrival distribution."""
