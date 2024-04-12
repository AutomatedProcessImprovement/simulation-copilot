import sqlalchemy as sa

from simulation_copilot.prosimos_relational.base import _Base


class CaseArrival(_Base):
    """The calendar of case arrivals and distribution of inter-arrival times."""

    __tablename__ = "case_arrival"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    calendar_id = sa.Column(sa.String, sa.ForeignKey("calendar.id"), nullable=False)
    """The calendar of case arrivals."""
    inter_arrival_distribution_id = sa.Column(sa.String, sa.ForeignKey("distribution.id"), nullable=False)
    """The distribution of inter-arrival times for cases."""
    simulation_model_id = sa.Column(sa.String, sa.ForeignKey("simulation_model.id"), nullable=False)
    """The simulation model to which this case arrival model belongs."""
