from sqlalchemy.orm import Session

from simulation_copilot.prosimos_model.resource_model import Day
from simulation_copilot.prosimos_relational_model import (
    SimulationModel,
    Gateway,
    SequenceFlow,
    Distribution,
    DistributionParameter,
    Calendar,
    CalendarInterval,
    CaseArrival,
    Activity,
    ActivityResourceDistribution,
    ResourceProfile,
    Resource,
)


class BaseRepository:
    def __init__(self, session: Session):
        self.session = session


class SimulationModelRepository(BaseRepository):
    """Repository for the simulation model."""

    def create(self):
        model = SimulationModel()
        self.session.add(model)
        self.session.commit()
        return model

    def get(self, id: int):
        return self.session.query(SimulationModel).filter(SimulationModel.id == id).first()

    def delete(self, id: int):
        model = self.get(id)
        if model:
            self.session.delete(model)
            self.session.commit()


class GatewayRepository(BaseRepository):
    """Repository for the gateways and their sequence flows in the simulation model."""

    def create(self, model_id: int, bpmn_id: str):
        model = self.session.query(SimulationModel).filter(SimulationModel.id == model_id).first()
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        gateway = Gateway(simulation_model_id=model_id, bpmn_id=bpmn_id)
        model.gateways.append(gateway)
        self.session.commit()
        return gateway

    def get(self, id: int):
        return self.session.query(Gateway).filter(Gateway.id == id).first()

    def get_sequence_flow(self, id: int):
        return self.session.query(SequenceFlow).filter(SequenceFlow.id == id).first()

    def add_sequence_flow(self, gateway_id: int, bpmn_id: str, probability: float):
        gateway = self.session.query(Gateway).filter(Gateway.id == gateway_id).first()
        if not gateway:
            raise ValueError(f"Gateway with ID {gateway_id} not found.")
        flow = SequenceFlow(source_gateway_id=gateway_id, bpmn_id=bpmn_id, probability=probability)
        gateway.outgoing_sequence_flows.append(flow)
        self.session.commit()
        return flow


class DistributionRepository(BaseRepository):
    """Repository for the distributions in the simulation model."""

    def create(self, name: str):
        distribution = Distribution(name=name)
        self.session.add(distribution)
        self.session.commit()
        return distribution

    def add_parameter(self, distribution_id: int, name: str, value: float):
        distribution = self.session.query(Distribution).filter(Distribution.id == distribution_id).first()
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        parameter = DistributionParameter(name=name, value=value)
        distribution.parameters.append(parameter)
        self.session.commit()
        return parameter


class CalendarRepository(BaseRepository):
    """Repository for the calendars in the simulation model."""

    def create(self):
        calendar = Calendar()
        self.session.add(calendar)
        self.session.commit()
        return calendar

    def add_interval(
        self,
        calendar_id: int,
        start_day: Day,
        end_day: Day,
        start_hour: int,
        end_hour: int,
        start_minute: int,
        end_minute: int,
    ):
        calendar = self.session.query(Calendar).filter(Calendar.id == calendar_id).first()
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        interval = CalendarInterval(
            start_day=start_day,
            end_day=end_day,
            start_hour=start_hour,
            end_hour=end_hour,
            start_minute=start_minute,
            end_minute=end_minute,
        )
        calendar.intervals.append(interval)
        self.session.commit()
        return interval


class CaseArrivalRepository(BaseRepository):
    """Repository for the case arrival times in the simulation model."""

    def create(self, calendar_id: int, distribution_id: int, model_id: int):
        arrival = CaseArrival(
            calendar_id=calendar_id, inter_arrival_distribution_id=distribution_id, simulation_model_id=model_id
        )
        self.session.add(arrival)
        self.session.commit()
        return arrival


class ActivityRepository(BaseRepository):
    """Repository for the activities in the simulation model."""

    def create(self, bpmn_id: str, resource_id: int, name: str):
        activity = Activity(bpmn_id=bpmn_id, resource_id=resource_id, name=name)
        self.session.add(activity)
        self.session.commit()
        return activity


class ActivityResourceDistributionRepository(BaseRepository):
    """Repository for the activity resource distributions in the simulation model."""

    def create(self, activity_id: int, resource_id: int, distribution_id: int):
        activity_resource_distribution = ActivityResourceDistribution(
            activity_id=activity_id, resource_id=resource_id, distribution_id=distribution_id
        )
        self.session.add(activity_resource_distribution)
        self.session.commit()
        return activity_resource_distribution


class ResourceProfileRepository(BaseRepository):
    """Repository for the resource profiles in the simulation model."""

    def create(self, name: str, model_id: int):
        profile = ResourceProfile(name=name, simulation_model_id=model_id)
        self.session.add(profile)
        self.session.commit()
        return profile

    def add_resource(
        self, profile_id: int, bpmn_id: str, name: str, amount: int, cost_per_hour: float, calendar_id: int
    ):
        profile = self.session.query(ResourceProfile).filter(ResourceProfile.id == profile_id).first()
        if not profile:
            raise ValueError(f"Resource profile with ID {profile_id} not found.")
        resource = Resource(
            bpmn_id=bpmn_id, name=name, amount=amount, cost_per_hour=cost_per_hour, calendar_id=calendar_id
        )
        profile.resources.append(resource)
        self.session.commit()
        return resource


class ProsimosRelationalRepository:
    """Repository for the Prosimos relational simulation model."""

    def __init__(self, session: Session):
        self.session = session
        self.simulation_model = SimulationModelRepository(session)
        self.gateway = GatewayRepository(session)
        self.distribution = DistributionRepository(session)
        self.calendar = CalendarRepository(session)
        self.case_arrival = CaseArrivalRepository(session)
        self.activity = ActivityRepository(session)
        self.activity_resource_distribution = ActivityResourceDistributionRepository(session)
        self.resource_profile = ResourceProfileRepository(session)
