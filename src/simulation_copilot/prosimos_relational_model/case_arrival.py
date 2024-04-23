"""Case arrival model which consists of the arrival calendar and inter-arrival distribution."""
import sqlalchemy as sa
from sqlalchemy.orm import Mapped

from simulation_copilot.prosimos_relational_model.base import _Base


class CaseArrival(_Base):
    """The calendar of case arrivals and distribution of inter-arrival times."""

    # pylint: disable=too-few-public-methods

    __tablename__ = "case_arrival"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    calendar_id = sa.Column(sa.Integer, sa.ForeignKey("calendar.id"), nullable=False)
    """The calendar of case arrivals."""
    inter_arrival_distribution_id = sa.Column(sa.Integer, sa.ForeignKey("distribution.id"), nullable=False)
    """The distribution of inter-arrival times for cases."""
    simulation_model_id = sa.Column(sa.Integer, sa.ForeignKey("simulation_model.id"), nullable=False)
    """The simulation model to which this case arrival model belongs."""

    inter_arrival_distribution: Mapped["Distribution"] = sa.orm.relationship("Distribution")
    """The distribution of inter-arrival times for cases."""
    calendar: Mapped["Calendar"] = sa.orm.relationship("Calendar")
    """The calendar of case arrivals."""
