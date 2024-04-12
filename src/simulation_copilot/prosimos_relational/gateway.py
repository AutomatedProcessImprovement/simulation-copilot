import sqlalchemy as sa

from simulation_copilot.prosimos_relational.base import _Base


class SequenceFlow(_Base):
    __tablename__ = "sequence_flows"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    probability = sa.Column(sa.Float, nullable=False)
    source_gateway_id = sa.Column(sa.String, sa.ForeignKey("gateways.id"), nullable=False)


class Gateway(_Base):
    __tablename__ = "gateways"

    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    bpmn_id = sa.Column(sa.String, nullable=False)
    outgoing_sequence_flows = sa.orm.relationship("SequenceFlow", backref="source_gateway")
    simulation_model_id = sa.Column(sa.String, sa.ForeignKey("simulation_models.id"), nullable=False)
