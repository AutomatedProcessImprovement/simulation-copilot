"""
Prosimos-to-Relational Adapter converts the Prosimos simulation model to the relational version.
"""

from pathlib import Path
from typing import Optional

from pix_framework.discovery.case_arrival import CaseArrivalModel
from pix_framework.discovery.gateway_probabilities import GatewayProbabilities
from pix_framework.discovery.resource_calendar_and_performance.crisp.resource_calendar import (
    RCalendar,
)
from pix_framework.discovery.resource_model import ResourceModel
from pix_framework.io.bpmn import get_activities_ids_by_name_from_bpmn
from pix_framework.statistics.distribution import DurationDistribution
from sqlalchemy.orm import Session

from simulation_copilot.prosimos_model.simulation_model import BPSModel
from simulation_copilot.prosimos_relational_model import SimulationModel
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService


def create_simulation_model_from_pix(
    session: Session, model: dict, process_model_path: Optional[Path]
) -> SimulationModel:
    """
    Converts the PIX simulation model represented as JSON (Python dict) to the relational simulation model.
    """
    service = ProsimosRelationalService(session)

    pix_model = BPSModel.from_prosimos_format(attributes=model, process_model=process_model_path)

    relational_model = service.create_simulation_model()

    activities_ids_by_name = get_activities_ids_by_name_from_bpmn(process_model_path)
    activities_names_by_id = {v: k for k, v in activities_ids_by_name.items()}

    if pix_model.gateway_probabilities:
        _create_gateways(service, relational_model.id, pix_model.gateway_probabilities)

    if pix_model.case_arrival_model:
        _create_case_arrival(service, relational_model.id, pix_model.case_arrival_model)

    if pix_model.resource_model:
        _create_resource_profiles(service, relational_model.id, pix_model.resource_model, activities_names_by_id)

    relational_model = service.get_simulation_model(relational_model.id)  # get the updated model from the database
    return relational_model


def _create_gateways(
    service: ProsimosRelationalService, model_id: int, gateway_probabilities: list[GatewayProbabilities]
):
    for gateway_probability in gateway_probabilities:
        service.create_gateway_with_sequence_flows(
            model_id=model_id,
            gateway_bpmn_id=gateway_probability.gateway_id,
            flows=[
                {"bpmn_id": flow.path_id, "probability": flow.probability}
                for flow in gateway_probability.outgoing_paths
            ],
        )


def _create_case_arrival(service: ProsimosRelationalService, model_id: int, case_arrival_model: CaseArrivalModel):
    calendar = service.create_calendar_with_intervals(
        intervals=_pix_calendar_to_intervals(case_arrival_model.case_arrival_calendar)
    )
    pix_distribution = DurationDistribution.from_dict(case_arrival_model.inter_arrival_times)
    distribution = service.create_distribution_with_parameters(
        name=case_arrival_model.inter_arrival_times["distribution_name"],
        parameters=_pix_distribution_to_relational_distribution_parameters(pix_distribution),
    )
    service.create_case_arrival(
        model_id=model_id,
        calendar_id=calendar.id,
        distribution_id=distribution.id,
    )


def _create_resource_profiles(
    service: ProsimosRelationalService,
    model_id: int,
    resource_model: ResourceModel,
    activities_names_by_id: dict[str, str],
):
    # create resource calendars and map them to relational calendars
    calendars = {}  # calendar_id -> relational_calendar_id
    for calendar in resource_model.resource_calendars:  # we expect RCalendar, not FuzzyResourceCalendar
        if not isinstance(calendar, RCalendar):
            raise ValueError("Only RCalendar from the PIX framework is supported")
        intervals = _pix_calendar_to_intervals(calendar)
        relational_calendar = service.create_calendar_with_intervals(intervals)
        calendars[calendar.calendar_id] = relational_calendar.id

    # collect resources
    resources = {}
    for resource_profile in resource_model.resource_profiles:
        for resource in resource_profile.resources:
            if resource.id in resources:
                # process each resource only once, there might be duplicates across profiles
                continue
            resource = {
                "bpmn_id": resource.id,
                "name": resource.name,
                "amount": resource.amount,
                "cost_per_hour": resource.cost_per_hour,
                "calendar_id": calendars[resource.calendar_id],
                "activity_distributions": [],
            }
            resources[resource["bpmn_id"]] = resource

    # add activity distributions to the resources dict
    for activity_resource_distribution in resource_model.activity_resource_distributions:
        for resource_distribution in activity_resource_distribution.activity_resources_distributions:
            activity_distribution = {
                "activity_name": activities_names_by_id[activity_resource_distribution.activity_id],
                "activity_bpmn_id": activity_resource_distribution.activity_id,
                "distribution": {
                    "name": resource_distribution.distribution["distribution_name"],
                    "parameters": _pix_distribution_to_relational_distribution_parameters(
                        DurationDistribution.from_dict(resource_distribution.distribution)
                    ),
                },
            }
            resources[resource_distribution.resource_id]["activity_distributions"].append(activity_distribution)

    # create resource profiles
    for resource_profile in resource_model.resource_profiles:
        profile_resources = [resources[resource.id] for resource in resource_profile.resources]
        service.create_resource_profile_with_resources(
            model_id=model_id,
            name=resource_profile.name,
            resources=profile_resources,
        )


def _prosimos_calendar_start_time_to_dict(time: str) -> dict:
    hour, minute = _prosimos_calendar_time_to_tuple(time)
    return {
        "start_hour": hour,
        "start_minute": minute,
    }


def _prosimos_calendar_end_time_to_dict(time: str) -> dict:
    hour, minute = _prosimos_calendar_time_to_tuple(time)
    return {
        "end_hour": hour,
        "end_minute": minute,
    }


def _prosimos_calendar_time_to_tuple(time: str) -> tuple:
    parts = time.split(":")
    hour = int(parts[0])
    minute = int(parts[1])
    return hour, minute


def _pix_distribution_to_relational_distribution_parameters(
    distribution: DurationDistribution,
) -> list[dict]:
    name = distribution.type.value
    if name == "uniform":
        return [
            {"name": "min", "value": distribution.min},
            {"name": "max", "value": distribution.max},
        ]
    if name == "norm":
        return [
            {"name": "mean", "value": distribution.mean},
            {"name": "std", "value": distribution.std},
            {"name": "min", "value": distribution.min},
            {"name": "max", "value": distribution.max},
        ]
    if name == "expon":
        return [
            {"name": "mean", "value": distribution.mean},
            {"name": "min", "value": distribution.min},
            {"name": "max", "value": distribution.max},
        ]
    if name in ("lognorm", "gamma"):
        return [
            {"name": "mean", "value": distribution.mean},
            {"name": "var", "value": distribution.var},
            {"name": "min", "value": distribution.min},
            {"name": "max", "value": distribution.max},
        ]
    if name == "fix":
        return [
            {"name": "mean", "value": distribution.mean},
        ]
    raise ValueError(f"Unknown distribution type: {name}")


def _pix_calendar_to_intervals(calendar: RCalendar) -> list[dict]:
    return [
        {"start_day": interval["from"], "end_day": interval["to"]}
        | _prosimos_calendar_start_time_to_dict(interval["beginTime"])
        | _prosimos_calendar_end_time_to_dict(interval["endTime"])
        for interval in calendar.intervals_to_json()
    ]
