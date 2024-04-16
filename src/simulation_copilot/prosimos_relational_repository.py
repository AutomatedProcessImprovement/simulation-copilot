from sqlalchemy.orm import Session

from simulation_copilot.prosimos_relational_model import (
    SimulationModel,
    Gateway,
    SequenceFlow,
    Distribution,
    DistributionParameter,
    Calendar,
    CaseArrival,
    Activity,
    ActivityResourceDistribution,
    ResourceProfile,
    Resource,
    Base,
)


class BaseRepository:
    def __init__(self, session: Session):
        self.session = session

    def delete_all(self):
        for table in reversed(Base.metadata.sorted_tables):
            self.session.execute(table.delete())
            self.session.commit()


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
        gateway = self.get(gateway_id)
        if not gateway:
            raise ValueError(f"Gateway with ID {gateway_id} not found.")
        flow = SequenceFlow(source_gateway_id=gateway_id, bpmn_id=bpmn_id, probability=probability)
        gateway.outgoing_sequence_flows.append(flow)
        self.session.commit()
        return flow

    def add_sequence_flows(self, gateway_id: int, flows: list):
        gateway = self.get(gateway_id)
        if not gateway:
            raise ValueError(f"Gateway with ID {gateway_id} not found.")
        for flow in flows:
            gateway.outgoing_sequence_flows.append(
                SequenceFlow(bpmn_id=flow["bpmn_id"], probability=flow["probability"])
            )
        self.session.commit()


class DistributionRepository(BaseRepository):
    """Repository for the distributions in the simulation model."""

    def create(self, name: str):
        distribution = Distribution(name=name)
        self.session.add(distribution)
        self.session.commit()
        return distribution

    def get(self, id: int):
        return self.session.query(Distribution).filter(Distribution.id == id).first()

    def add_parameter(self, distribution_id: int, name: str, value: float):
        distribution = self.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        parameter = DistributionParameter(name=name, value=value)
        distribution.parameters.append(parameter)
        self.session.commit()
        return parameter

    def add_parameters(self, distribution_id: int, parameters: list):
        distribution = self.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        for parameter in parameters:
            distribution.parameters.append(DistributionParameter(name=parameter["name"], value=parameter["value"]))
        self.session.commit()

    def delete(self, id: int):
        distribution = self.get(id)
        if distribution:
            self.session.delete(distribution)
            self.session.commit()


class CalendarRepository(BaseRepository):
    """Repository for the calendars in the simulation model."""

    def create(self):
        calendar = Calendar()
        self.session.add(calendar)
        self.session.commit()
        return calendar

    def get(self, id: int):
        return self.session.query(Calendar).filter(Calendar.id == id).first()

    def delete(self, id: int):
        calendar = self.get(id)
        if calendar:
            self.session.delete(calendar)
            self.session.commit()


class CaseArrivalRepository(BaseRepository):
    """Repository for the case arrival times in the simulation model."""

    def create(self, calendar_id: int, distribution_id: int, model_id: int):
        arrival = CaseArrival(
            calendar_id=calendar_id,
            inter_arrival_distribution_id=distribution_id,
            simulation_model_id=model_id,
        )
        self.session.add(arrival)
        self.session.commit()
        return arrival

    def get(self, id: int):
        return self.session.query(CaseArrival).filter(CaseArrival.id == id).first()

    def delete(self, id: int):
        arrival = self.get(id)
        if arrival:
            self.session.delete(arrival)
            self.session.commit()


class ActivityRepository(BaseRepository):
    """Repository for the activities in the simulation model."""

    def create(self, bpmn_id: str, resource_id: int, name: str):
        activity = Activity(bpmn_id=bpmn_id, resource_id=resource_id, name=name)
        self.session.add(activity)
        self.session.commit()
        return activity

    def get(self, id: int):
        return self.session.query(Activity).filter(Activity.id == id).first()

    def delete(self, id: int):
        activity = self.get(id)
        if activity:
            self.session.delete(activity)
            self.session.commit()


class ActivityResourceDistributionRepository(BaseRepository):
    """Repository for the activity resource distributions in the simulation model."""

    def create(self, activity_id: int, resource_id: int, distribution_id: int):
        activity_resource_distribution = ActivityResourceDistribution(
            activity_id=activity_id,
            resource_id=resource_id,
            distribution_id=distribution_id,
        )
        self.session.add(activity_resource_distribution)
        self.session.commit()
        return activity_resource_distribution

    def get(self, id: int):
        return self.session.query(ActivityResourceDistribution).filter(ActivityResourceDistribution.id == id).first()

    def delete(self, id: int):
        distribution = self.get(id)
        if distribution:
            self.session.delete(distribution)
            self.session.commit()


class ResourceRepository(BaseRepository):
    """Repository for the resources in the simulation model."""

    def create(self, bpmn_id: str, name: str, calendar_id: int, amount: int = 1, cost_per_hour: float = 1) -> Resource:
        resource = Resource(
            bpmn_id=bpmn_id,
            name=name,
            amount=amount,
            cost_per_hour=cost_per_hour,
            calendar_id=calendar_id,
        )
        self.session.add(resource)
        self.session.commit()
        return resource

    def get(self, id: int) -> Resource:
        return self.session.query(Resource).filter(Resource.id == id).first()

    def delete(self, id: int):
        resource = self.get(id)
        if resource:
            self.session.delete(resource)
            self.session.commit()


class ResourceProfileRepository(BaseRepository):
    """Repository for the resource profiles in the simulation model."""

    def create(self, name: str, model_id: int):
        profile = ResourceProfile(name=name, simulation_model_id=model_id)
        self.session.add(profile)
        self.session.commit()
        return profile

    def get(self, id: int):
        return self.session.query(ResourceProfile).filter(ResourceProfile.id == id).first()

    def add_resource(
        self,
        profile_id: int,
        resource_id: int,
    ):
        profile = self.get(profile_id)
        if not profile:
            raise ValueError(f"Resource profile with ID {profile_id} not found.")

        resource = self.session.query(Resource).filter(Resource.id == resource_id).first()
        if not resource:
            raise ValueError(f"Resource with ID {resource_id} not found.")
        resource.profile_id = profile_id

        profile.resources.append(resource)

        self.session.commit()
        return profile

    def add_resources(self, profile_id: int, resources: list):
        profile = self.get(profile_id)
        if not profile:
            raise ValueError(f"Resource profile with ID {profile_id} not found.")
        for resource in resources:
            profile.resources.append(
                Resource(
                    bpmn_id=resource["bpmn_id"],
                    name=resource["name"],
                    amount=resource.get("amount") or 1,
                    cost_per_hour=resource.get("cost_per_hour") or 1,
                    calendar_id=resource["calendar_id"],
                )
            )
        self.session.commit()


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
        self.resource = ResourceRepository(session)
        self.resource_profile = ResourceProfileRepository(session)
