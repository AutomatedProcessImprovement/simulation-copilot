from uuid import uuid4

from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from simulation_copilot.prosimos_model.resource_model import (
    ActivityDistribution,
    Distribution,
    Resource,
    ResourceProfile,
)


class ActivityDistributionInput(BaseModel):
    activity_id: str = Field(description="The id of the activity")
    distribution: Distribution = Field(
        description="The distribution of the activity in the form of a name of the distribution and a list of parameters specific to the distribution"
    )


class ResourceInput(BaseModel):
    resource_name: str = Field(description="The name of the resource")
    amount: int = Field(description="The amount of the resource")
    cost_per_hour: float = Field(description="The cost per hour of the resource")
    calendar_id: str = Field(description="The id of the calendar")
    activities: list[ActivityDistributionInput] = Field(
        description="The distribution of the activity in the form of a name of the distribution and a list of parameters specific to the distribution"
    )


class GenerateResourceProfileInput(BaseModel):
    name: str = Field(description="The name of the resource profile")
    resources: list[ResourceInput] = Field(description="The resources with their assigned activities")


@tool("generate_resource_profile", args_schema=GenerateResourceProfileInput)
def generate_resource_profile(
    name: str,
    resources: list[ResourceInput],
) -> ResourceProfile:
    """
    Generate a resource profile with the given resources and their assigned activities.
    """
    return ResourceProfile(
        id=uuid4().hex,
        name=name,
        resources=[
            Resource(
                id=uuid4().hex,
                name=resource.resource_name,
                amount=resource.amount,
                cost_per_hour=resource.cost_per_hour,
                calendar_id=resource.calendar_id,
                assigned_activities=[
                    ActivityDistribution(
                        activity_id=activity.activity_id,
                        distribution=activity.distribution,
                    )
                    for activity in resource.activities
                ],
            )
            for resource in resources
        ],
    )
