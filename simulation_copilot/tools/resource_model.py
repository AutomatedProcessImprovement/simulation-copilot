from langchain.pydantic_v1 import BaseModel, Field
from langchain.tools import tool

from simulation_copilot.resource_model import Calendar, ResourceModel, ResourceProfile


class GenerateResourceModelInput(BaseModel):
    resource_profiles: list[ResourceProfile] = Field(
        description="The resource profiles with their assigned resources"
    )
    calendars: list[Calendar] = Field(description="The calendars of the resources")


@tool("generate_resource_model", args_schema=GenerateResourceModelInput)
def generate_resource_model(
    resource_profiles: list[ResourceProfile],
    calendars: list[Calendar],
) -> ResourceModel:
    """
    Generate a resource model with the given resource profiles and their corresponding calendars.
    """
    return ResourceModel(
        profiles=resource_profiles,
        calendars=calendars,
    )
