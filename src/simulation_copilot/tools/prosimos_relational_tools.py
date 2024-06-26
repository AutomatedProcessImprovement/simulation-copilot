"""Tools for answering high-level questions about a business process using the Prosimos relational simulation model.

Example of high-level questions:

- What if we increase or decrease the number of resources of a role?
"""

from pathlib import Path

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import tool

from simulation_copilot.database import get_session
from simulation_copilot.prosimos_relational_model import SimulationModel
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.prosimos_utils import (
    run_prosimos,
    get_resource_utilization_and_overall_statistics,
)

# pylint: disable=missing-class-docstring,global-statement

_session = get_session()
_service = ProsimosRelationalService(_session)

# Baseline performance of the initial simulation which should be set from the main script
# in the beginning of the user session.
_baseline_performance_report: str = ""

# Path to the BPMN file that is used in simulation. In this prototype, we work only with one simulation model
# at a time, so we simply use the module-level variable and update it from the main CLI script.
_process_path: Path


def set_baseline_performance_report(report: str):
    """Setter for the corresponding module variable."""
    global _baseline_performance_report
    _baseline_performance_report = report


def set_process_path(process_path: Path):
    """Setter for the corresponding module variable."""
    global _process_path
    _process_path = process_path


class QuerySimulationModelArgs(BaseModel):
    simulation_id: int = Field(description="The ID of the simulation model.")


class ChangeResourceAmountArgs(BaseModel):
    resource_id: int = Field(description="The ID of the resource.")
    amount: int = Field(description="The new amount of the resource.")


class NewDistributionArgs(BaseModel):
    name: str = Field(
        description="The name of the distribution. "
        "One of 'uniform', 'normal', 'fixed', 'exponential', 'lognormal', 'gamma'"
    )
    parameters: list[dict] = Field(
        description="A list of distribution parameters. "
        "Each parameter is a dictionary `{'name': 'mean', 'value': 0.5}`."
        "The following parameter names are supported: 'mean', 'stddev', 'var', 'min', 'max'."
        "Below are the required parameters for each distribution:"
        "- uniform: 'min', 'max'"
        "- normal: 'mean', 'stddev', 'min', 'max'"
        "- exponential: 'mean', 'min', 'max'"
        "- lognormal: 'mean', 'var', 'min', 'max'"
        "- gamma: 'mean', 'var', 'min', 'max'"
        "- fixed: 'mean'"
    )


class NewResourceActivityDistributionArgs(BaseModel):
    activity_name: str = Field(description="The name of the activity.")
    activity_bpmn_id: str = Field(description="The BPMN ID of the activity.")
    distribution: NewDistributionArgs = Field(description="The distribution of the resource for the activity.")


class NewResourceArgs(BaseModel):
    profile_id: int = Field(description="The ID of the profile.")
    bpmn_id: str = Field(description="The BPMN ID of the resource.")
    name: str = Field(description="The name of the resource.")
    amount: int = Field(description="The amount of the resource. Default is 1.")
    cost_per_hour: float = Field(description="The cost per hour of the resource. Default is 1.")
    calendar_id: int = Field(description="The ID of the availability calendar of the resource.")
    resource_activity_distributions: list[NewResourceActivityDistributionArgs] = Field(
        description="A list of resource activity distributions."
    )


class NewCalendarArgs(BaseModel):
    intervals: list[dict] = Field(
        description="A list of intervals. Each interval is a dictionary with the following keys:"
        "'start_day', 'end_day', 'start_hour', 'end_hour', 'start_minute', 'end_minute'."
        "A day is a string with the name of the day (e.g., 'Monday', 'Tuesday', etc)."
        "An hour is an integer from 0 to 23."
        "A minute is an integer from 0 to 59."
    )


class NewCaseArrivalArgs(BaseModel):
    simulation_model_id: int = Field("Simulation model ID in the database. Type: integer.")
    calendar_id: int = Field("Calendar ID in the database. Type: integer.")
    inter_arrival_distribution_id: int = Field("Inter-arrival distribution ID in the database. Type: integer.")


@tool("create_simulation_model")
def create_simulation_model() -> int:
    """Creates a new simulation model in the database with empty parameters and returns its ID."""
    return _service.create_simulation_model().id


@tool("get_simulation_model", args_schema=QuerySimulationModelArgs)
def get_simulation_model(simulation_id: int) -> SimulationModel:
    """Returns the simulation model with the given ID from the database."""
    return _service.get_simulation_model(simulation_id)


@tool("change_resource_amount", args_schema=ChangeResourceAmountArgs)
def change_resource_amount(resource_id: int, amount: int) -> bool:
    """Changes the amount of a resource in the simulation model.
    Returns True if the operation was successful.
    """
    resource = _service.repository.resource.get(resource_id)
    if resource is None:
        raise ValueError(f"Resource with ID {resource_id} not found.")
    resource.amount = amount
    _session.add(resource)
    _session.commit()
    return True


# pylint: disable=too-many-arguments
@tool("add_resource_to_profile", args_schema=NewResourceArgs)
def add_resource_to_profile(
    profile_id: int,
    bpmn_id: str,
    name: str,
    amount: int,
    cost_per_hour: float,
    calendar_id: int,
    resource_activity_distributions: list[dict],
) -> bool:
    """Adds a resource to a profile of the simulation model. Besides the resource parameters, it requires the resource
    availability calendar ID and a list of resource-activity distributions.
    Returns True if the operation was successful.
    """
    profile = _service.repository.resource_profile.get(profile_id)
    if profile is None:
        raise ValueError(f"Profile with ID {profile_id} not found.")
    # pylint: disable=duplicate-code
    resource = _service.create_resource_with_activity_distributions(
        bpmn_id=bpmn_id,
        name=name,
        amount=amount,
        cost_per_hour=cost_per_hour,
        calendar_id=calendar_id,
        activity_distributions=resource_activity_distributions,
    )
    profile.resources.append(resource)
    _session.add(profile)
    _session.commit()
    return True


@tool("remove_resource_from_profile_by_id")
def remove_resource_from_profile_by_id(resource_id: int) -> bool:
    """Removes a resource from a profile of the simulation model.
    Returns True if the operation was successful.
    """
    resource = _service.repository.resource.get(resource_id)
    if resource is None:
        raise ValueError(f"Resource with ID {resource_id} not found.")
    _session.delete(resource)
    _session.commit()
    return True


@tool("create_calendar_with_intervals", args_schema=NewCalendarArgs)
def create_calendar_with_intervals(intervals: list[dict]) -> int:
    """Creates a new availability calendar with intervals and returns its ID."""
    return _service.create_calendar_with_intervals(intervals).id


@tool("create_distribution", args_schema=NewDistributionArgs)
def create_distribution(name: str, parameters: list[dict]) -> int:
    """Creates a distribution object from the given arguments.
    Returns the ID of the distribution."""
    _ensure_all_distribution_parameters(name, parameters)
    return _service.create_distribution_with_parameters(name=name, parameters=parameters).id


@tool("add_case_arrival", args_schema=NewCaseArrivalArgs)
def add_case_arrival(simulation_model_id: int, calendar_id: int, inter_arrival_distribution_id: int) -> bool:
    """Adds case arrival model to the simulation model. Calendar and distribution must be created beforehand."""
    _service.create_case_arrival(
        model_id=simulation_model_id,
        calendar_id=calendar_id,
        distribution_id=inter_arrival_distribution_id,
    )
    return True


@tool("get_resource_id_by_name")
def get_resource_id_by_name(name: str) -> int:
    """Returns the ID of the resource with the given name."""
    resource = _service.repository.resource.get_by_name(name)
    if resource is None:
        raise ValueError(f"Resource with name {name} not found.")
    return resource.id


@tool("get_baseline_performance_report")
def get_baseline_performance_report() -> str:
    """Returns the baseline performance report of the simulation model before any changes."""
    report = f"Baseline performance report:\n{_baseline_performance_report}"  # marks the baseline report for LLM
    return report


@tool("generate_performance_report")
def generate_performance_report(model_id: int) -> str:
    """Runs a simulation given the simulation model ID and returns the performance report generated by the simulator.
    Returns the report as string."""
    report = run_prosimos(model_id=model_id, process_path=_process_path)
    report = get_resource_utilization_and_overall_statistics(report)
    report = f"New performance report:\n{report}"  # marks the new report for LLM, so it's not lost in the prompt
    return report


def _ensure_all_distribution_parameters(name: str, parameters: list[dict]):
    if name in ("fix", "fixed"):
        return
    # all other distributions must have min, max
    _ensure_min(parameters)
    _ensure_max(parameters)


def _ensure_max(parameters: list[dict]):
    mean = 0
    parameter_names = []
    for p in parameters:
        if p["name"] == "mean":
            mean = p["value"]
        parameter_names.append(p["name"])
    if "max" not in parameter_names:  # NOTE: if max is missing, we take mean as max
        parameters.append({"name": "max", "value": mean})


def _ensure_min(parameters: list[dict]):
    mean = 0
    parameter_names = []
    for p in parameters:
        if p["name"] == "mean":
            mean = p["value"]
        parameter_names.append(p["name"])
    if "min" not in parameter_names:  # NOTE: if min is missing, we take mean as min
        parameters.append({"name": "min", "value": mean})
