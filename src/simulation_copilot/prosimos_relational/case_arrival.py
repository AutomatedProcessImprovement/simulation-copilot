import sqlalchemy as sa

from simulation_copilot.prosimos_relational import Base


class CaseArrival(Base):
    """The calendar of case arrivals and distribution of inter-arrival times."""

    __tablename__ = "case_arrivals"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    calendar_id = sa.Column(sa.String, sa.ForeignKey("calendars.id"), nullable=False)
    """The calendar of case arrivals."""
    inter_arrival_distribution_id = sa.Column(sa.String, sa.ForeignKey("distributions.id"), nullable=False)
    """The distribution of inter-arrival times for cases."""
