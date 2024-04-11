from langchain.pydantic_v1 import BaseModel
from pix_framework.discovery.gateway_probabilities import GatewayProbabilities

from simulation_copilot.prosimos.resource_model import ResourceModel


class SimulationModel(BaseModel):
    """
    Simulation model collects all the settings required to run a business process simulator on the given simulation model.
    """

    resource_model: ResourceModel
    gateway_probabilities: list[GatewayProbabilities]
