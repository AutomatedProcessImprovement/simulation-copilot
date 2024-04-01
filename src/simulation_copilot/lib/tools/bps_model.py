from langchain.pydantic_v1 import BaseModel, Field
from langchain_core.tools import StructuredTool
from pix_framework.discovery.gateway_probabilities import GatewayProbabilities

from simulation_copilot.lib.bps_model_simplified import SimulationModel
from simulation_copilot.lib.resource_model import ResourceModel


class SimulationModelInput(BaseModel):
    """
    The input schema for the generate_bps_model tool. It requires a resource model and gateway probabilities.
    The resource model is a collection of resource profiles and calendars.
    The gateway probabilities are the probabilities of the outgoing paths from the gateways.

    Example:
    ```
    {
        "resource_model": {
            "profiles": [
                {
                    "id": "a0d5d6f5f4d5d4f5",
                    "resources": [
                        {
                            "id": "a0d5d6f5f4d5d4f5",
                            "name": "resource1",
                            "amount": 1,
                            "cost_per_hour": 10.0,
                            "calendar_id": "a0d5d6f5f4d5d4f5",
                            "assigned_activities": [
                                {
                                    "activity_id": "a0d5d6f5f4d5d4f5",
                                    "distribution": {
                                        "name": "normal",
                                        "parameters": [1.0, 1.0]
                                    }
                                }
                            ]
                        }
                    ]
                }
            ],
            "calendars": [
                {
                    "id": "a0d5d6f5f4d5d4f5",
                    "name": "calendar1",
                    "working_hours": {
                        "start": "2022-01-01T00:00:00Z",
                        "end": "2022-01-01T23:59:59Z"
                    }
                }
            ]
        },
        "gateway_probabilities": [
            {
                "id": "a0d5d6f5f4d5d4f5",
                "probability": 0.5
            }
        ]
    }
    ```
    """

    resource_model: ResourceModel = Field(description="The resource model")
    gateway_probabilities: list[GatewayProbabilities] = Field(
        description="The gateway probabilities"
    )


def _generate_bps_model(
    resource_model: ResourceModel, gateway_probabilities: list[GatewayProbabilities]
) -> SimulationModel:
    """
    Generate a business process simulation model with the given resource model and gateway probabilities.
    """
    return SimulationModel(
        resource_model=resource_model,
        gateway_probabilities=gateway_probabilities,
    )


generate_bps_model = StructuredTool.from_function(
    func=_generate_bps_model,
    args_schema=SimulationModelInput,
    return_direct=True,
    return_schema=SimulationModel,
    name="generate_bps_model",
    description="Generate a business process simulation model with the given resource model and gateway probabilities.",
)
