from typing import List

from pix_framework.discovery.gateway_probabilities import GatewayProbabilities, PathProbability
from sqlalchemy.orm import Session

from simulation_copilot.prosimos_model.simulation_model import BPSModel
from simulation_copilot.prosimos_relational_model import SimulationModel


def query_simulation_model(session: Session, model_id: int) -> BPSModel:
    """Query the simulation model and its relationships with the given ID from the database and compose a BPS model."""

    sql_model = session.query(SimulationModel).filter(SimulationModel.id == model_id).first()
    if not sql_model:
        raise ValueError(f"Model with ID {model_id} not found.")

    model = BPSModel()

    gateway_probabilities: List[GatewayProbabilities] = []
    for gateway in sql_model.gateways:
        gateway_probabilities.append(
            GatewayProbabilities(
                gateway_id=gateway.bpmn_id,
                outgoing_paths=[
                    PathProbability(path_id=path.bpmn_id, probability=path.probability)
                    for path in gateway.outgoing_sequence_flows
                ],
            )
        )
    model.gateway_probabilities = gateway_probabilities

    return model
