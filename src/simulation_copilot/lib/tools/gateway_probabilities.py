from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool
from pix_framework.discovery.gateway_probabilities import (
    GatewayProbabilities,
    PathProbability,
)


class GatewayInput(BaseModel):
    gateway_id: str = Field(description="ID of the gateway")
    outgoing_paths: list[PathProbability] = Field(
        description="Outgoing paths from the gateway with their probabilities"
    )


class GatewayProbabilitiesInput(BaseModel):
    gateway_settings: list[GatewayInput] = Field(
        description="The gateway settings with their outgoing paths and probabilities"
    )


@tool(
    "generate_gateway_probabilities",
    args_schema=GatewayProbabilitiesInput,
)
def generate_gateway_probabilities(
    gateway_settings: list[GatewayInput],
) -> list[GatewayProbabilities]:
    """
    Generate gateway probabilities for the given gateway.
    """
    return [
        GatewayProbabilities(
            gateway_id=setting.gateway_id,
            outgoing_paths=setting.outgoing_paths,
        )
        for setting in gateway_settings
    ]
