"""
Relational simulation model main class.

The relational simulation model is a version of the Prosimos model that is stored in a relational database.
"""
import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from simulation_copilot.prosimos_relational_model import CaseArrival
from simulation_copilot.prosimos_relational_model.base import _Base
from simulation_copilot.prosimos_relational_model.gateway import Gateway
from simulation_copilot.prosimos_relational_model.resource_profile import ResourceProfile


class SimulationModel(_Base):
    """
    The simulation model with its components.

    NOTE: Only a fraction of the Prosimos model is supported: resource profiles, gateways, and case arrival.
    """

    # pylint: disable=too-few-public-methods

    __tablename__ = "simulation_model"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)

    resource_profiles = sa.orm.relationship(ResourceProfile, backref="simulation_model", cascade="all, delete-orphan")
    """Resource profiles with resources and their assigned activities."""
    gateways = sa.orm.relationship(Gateway, backref="simulation_model", cascade="all, delete-orphan")
    """Gateways, their probabilities and sequence flows."""
    case_arrival: Mapped[CaseArrival] = sa.orm.relationship(
        CaseArrival, backref="simulation_model", cascade="all, delete-orphan"
    )  # one-to-one relationship
    """The calendar of case arrivals and distribution of inter-arrival times."""
