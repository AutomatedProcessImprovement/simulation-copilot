import sqlalchemy as sa
import sqlalchemy.orm

from simulation_copilot.prosimos_relational_model.base import _Base


class SequenceFlow(_Base):
    """A sequence flow in a BPMN model that connects activities and gateways."""

    __tablename__ = "sequence_flow"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    """The BPMN ID of the sequence flow from the BPMN model."""
    probability = sa.Column(sa.Float, nullable=False)
    """The probability of this sequence flow being taken."""
    source_gateway_id = sa.Column(sa.Integer, sa.ForeignKey("gateway.id"), nullable=False)
    """The gateway from which this sequence flow originates."""


class Gateway(_Base):
    """A gateway in a BPMN model that splits or joins the flow of tokens."""

    __tablename__ = "gateway"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    """The BPMN ID of the gateway from the BPMN model."""
    outgoing_sequence_flows = sa.orm.relationship(SequenceFlow, backref="source_gateway")
    """The sequence flows that leave this gateway."""
    simulation_model_id = sa.Column(sa.Integer, sa.ForeignKey("simulation_model.id"), nullable=False)
    """The simulation model to which this gateway belongs."""
