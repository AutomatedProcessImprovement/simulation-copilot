"""Prosimos Relational Model to Prosimos Model adapter.

It converts relational types to the Prosimos format.
"""

from pix_framework.discovery.case_arrival import CaseArrivalModel as PIXCaseArrivalModel
from pix_framework.discovery.gateway_probabilities import (
    GatewayProbabilities as PIXGatewayProbabilities,
    PathProbability as PIXPathProbability,
)
from pix_framework.discovery.resource_calendar_and_performance.crisp.resource_calendar import (
    RCalendar as PIXCalendar,
)
from pix_framework.discovery.resource_calendar_and_performance.resource_activity_performance import (
    ResourceDistribution as PIXResourceDistribution,
    ActivityResourceDistribution as PIXActivityResourceDistribution,
)
from pix_framework.discovery.resource_model import ResourceModel as PIXResourceModel
from pix_framework.discovery.resource_profiles import Resource as PIXResource
from pix_framework.discovery.resource_profiles import (
    ResourceProfile as PIXResourceProfile,
)
from pix_framework.statistics.distribution import (
    DurationDistribution as PIXDurationDistribution,
)
from sqlalchemy.orm import Session

from simulation_copilot.database import get_session
from simulation_copilot.prosimos_model.simulation_model import BPSModel
from simulation_copilot.prosimos_relational_model import (
    Gateway,
    Calendar,
    Distribution,
    Resource,
    ActivityResourceDistribution,
    ResourceProfile,
)
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService


def print_all_simulation_models():
    """Converts relational simulation models to BPSModel and prints out to stdout."""
    session = get_session()
    service = ProsimosRelationalService(session)
    sql_models = service.get_all_simulation_models()
    for model in sql_models:
        pix_model = create_simulation_model_from_relational_data(session, model.id)
        print("\nPIX simulation model dump:")
        print(f"Model ID: {model.id}")
        print(pix_model)


def create_simulation_model_from_relational_data(session: Session, model_id: int) -> BPSModel:
    """
    Query the simulation model and its relationships with the given ID from the database and compose a BPS model.
    """
    service = ProsimosRelationalService(session)

    sql_model = service.get_simulation_model(model_id)
    if not sql_model:
        raise ValueError(f"Model with ID {model_id} not found.")

    model = BPSModel()

    # gateways
    if sql_model.gateways:
        pix_gateway_probabilities = [_gateway_to_pix(gateway) for gateway in sql_model.gateways]
        model.gateway_probabilities = pix_gateway_probabilities

    # case arrival
    if sql_model.case_arrival:
        arrival_calendar = service.get_calendar(sql_model.case_arrival.calendar_id)
        arrival_distribution = service.get_distribution(sql_model.case_arrival.inter_arrival_distribution_id)
        pix_case_arrival = _case_arrival_to_pix(arrival_calendar, arrival_distribution)
        model.case_arrival_model = pix_case_arrival

    # resource model
    if sql_model.resource_profiles:
        pix_resource_model = _resource_model_to_pix(sql_model.resource_profiles, service)
        model.resource_model = pix_resource_model

    return model


def _resource_model_to_pix(resource_profiles: list[ResourceProfile], service: ProsimosRelationalService):
    # processing resource profiles, resource calendars, and activity resource distributions in one loop
    # to avoid multiple loops over the same data
    pix_resource_profiles = []
    resource_calendars_map = {}
    activity_resource_distributions_map = {}
    for profile in resource_profiles:
        # collect resources for the profile
        resources = []

        for resource in profile.resources:
            # collect resources for the profile
            resources.append(_resource_to_pix(resource))
            # prepare resource calendars map for processing after this loop
            # NOTE: we assume each resource has a single calendar
            resource_calendars_map[resource.calendar_id] = True
            # prepare activity resource distributions map for processing after this loop
            for activity_resource_distribution in resource.assigned_activities:
                resource_distribution = _resource_distribution_to_pix(
                    activity_resource_distribution, resource.id, service
                )
                activity = service.get_activity(activity_resource_distribution.activity_id)
                if activity.id not in activity_resource_distributions_map:
                    activity_resource_distributions_map[activity.id] = [resource_distribution]
                else:
                    activity_resource_distributions_map[activity.id].append(resource_distribution)
                    # finish collecting resource profiles
        pix_resource_profiles.append(
            PIXResourceProfile(
                id=str(profile.id),
                name=profile.name,
                resources=resources,
            )
        )
    # finish processing resource calendars
    pix_resource_calendars = [
        _calendar_to_pix(service.get_calendar(calendar_id)) for calendar_id in resource_calendars_map
    ]
    # finish processing activity resource distributions
    pix_activity_resource_distributions = [
        PIXActivityResourceDistribution(
            activity_id=str(activity_id),
            activity_resources_distributions=distribution,
        )
        for (activity_id, distribution) in activity_resource_distributions_map.items()
    ]
    resource_model = PIXResourceModel(
        resource_calendars=pix_resource_calendars,
        resource_profiles=pix_resource_profiles,
        activity_resource_distributions=pix_activity_resource_distributions,
    )
    return resource_model


def _gateway_to_pix(gateway: Gateway) -> PIXGatewayProbabilities:
    return PIXGatewayProbabilities(
        gateway_id=gateway.bpmn_id,
        outgoing_paths=[
            PIXPathProbability(path_id=path.bpmn_id, probability=path.probability)
            for path in gateway.outgoing_sequence_flows
        ],
    )


def _case_arrival_to_pix(calendar: Calendar, distribution: Distribution) -> PIXCaseArrivalModel:
    return PIXCaseArrivalModel(
        case_arrival_calendar=_calendar_to_pix(calendar),
        inter_arrival_times=_distribution_to_pix(distribution).to_prosimos_distribution(),
    )


def _calendar_to_pix(calendar: Calendar) -> PIXCalendar:
    d = {
        "id": calendar.id,
        "time_periods": [
            {
                "from": interval.start_day.value.upper(),
                "to": interval.end_day.value.upper(),
                "beginTime": f"{interval.start_hour}:{interval.start_minute}",
                "endTime": f"{interval.end_hour}:{interval.end_minute}",
            }
            for interval in calendar.intervals
        ],
    }
    return PIXCalendar.from_dict(d)


def _distribution_to_pix(distribution: Distribution) -> PIXDurationDistribution:
    d = PIXDurationDistribution(
        name=distribution.name,
    )
    for parameter in distribution.parameters:
        if parameter.name == "mean":
            d.mean = parameter.value
        elif parameter.name == "var":
            d.var = parameter.value
        elif parameter.name == "std":
            d.std = parameter.value
        elif parameter.name == "min":
            d.min = parameter.value
        elif parameter.name == "max":
            d.max = parameter.value
        else:
            raise ValueError(f"Unknown distribution parameter: {parameter.name}")
    return d


def _resource_to_pix(resource: Resource) -> PIXResource:
    return PIXResource(
        id=str(resource.id),
        name=resource.name,
        amount=resource.amount,
        cost_per_hour=resource.cost_per_hour,
        calendar_id=str(resource.calendar_id),
        assigned_tasks=[],
    )


def _resource_distribution_to_pix(
    activity_resource_distribution: ActivityResourceDistribution,
    resource_id: int,
    service: ProsimosRelationalService,
) -> PIXResourceDistribution:
    distribution = service.get_distribution(activity_resource_distribution.distribution_id)
    return PIXResourceDistribution(
        resource_id=str(resource_id),
        distribution=_distribution_to_pix(distribution).to_prosimos_distribution(),
    )
