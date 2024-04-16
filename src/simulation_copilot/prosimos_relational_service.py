from sqlalchemy.orm import Session

from simulation_copilot.prosimos_relational_model import (
    Calendar,
    CalendarInterval,
    Gateway,
    SequenceFlow,
    SimulationModel,
    Distribution,
    CaseArrival,
    Activity,
    Resource,
    ActivityResourceDistribution,
    ResourceProfile,
)
from simulation_copilot.prosimos_relational_repository import (
    ProsimosRelationalRepository,
)


class ProsimosRelationalService:
    """Service for the Prosimos relational database."""

    def __init__(self, session: Session):
        self.repository = ProsimosRelationalRepository(session)

    def create_simulation_model(self) -> SimulationModel:
        """Create a simulation model."""
        return self.repository.simulation_model.create()

    def get_simulation_model(self, model_id: int) -> SimulationModel:
        """Get a simulation model."""
        return self.repository.simulation_model.get(model_id)

    def delete_simulation_model(self, model_id: int):
        """Delete a simulation model."""
        self.repository.simulation_model.delete(model_id)

    def create_gateway_with_sequence_flows(self, model_id: int, gateway_bpmn_id: str, flows: list[dict]) -> Gateway:
        """Create a gateway with a list of sequence flows.
        Flows must be a list of dictionaries with keys 'bpmn_id' and 'probability'."""
        model = self.repository.simulation_model.get(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")

        if self.repository.session.in_transaction():  # commit the current transaction if there is one
            self.repository.session.commit()

        with self.repository.session.begin():
            gateway = Gateway(simulation_model_id=model_id, bpmn_id=gateway_bpmn_id)
            model.gateways.append(gateway)
            for flow in flows:
                gateway.outgoing_sequence_flows.append(
                    SequenceFlow(
                        source_gateway_id=gateway.id,
                        bpmn_id=flow["bpmn_id"],
                        probability=flow["probability"],
                    )
                )
            self.repository.session.add(gateway)
            self.repository.session.add_all(gateway.outgoing_sequence_flows)
        return gateway

    def create_distribution_with_parameters(self, name: str, parameters: list[dict]) -> Distribution:
        """Create a distribution with a list of parameters.
        Parameters must be a list of dictionaries with keys 'name' and 'value'.

        The following distribution names are supported:
        'uniform', 'normal' ('norm'), 'exponential' ('expon'), 'lognormal' ('lognorm'), 'gamma', 'fixed' ('fix').

        The parameters for each distribution are as follows:
        - uniform: 'min', 'max'
        - normal: 'mean', 'stddev', 'min', 'max'
        - exponential: 'mean', 'min', 'max'
        - lognormal: 'mean', 'var', 'min', 'max'
        - gamma: 'mean', 'var', 'min', 'max'
        - fixed: 'mean'
        """
        distribution = self.repository.distribution.create(name)
        self.repository.distribution.add_parameters(distribution_id=distribution.id, parameters=parameters)
        return distribution

    def get_distribution(self, distribution_id: int) -> Distribution:
        """Get a distribution."""
        return self.repository.distribution.get(distribution_id)

    def delete_distribution(self, distribution_id: int):
        """Delete a distribution."""
        self.repository.distribution.delete(distribution_id)

    def create_calendar_with_intervals(self, intervals: list[dict]) -> Calendar:
        """Create a calendar with a list of intervals.
        Intervals must be a list of dictionaries with keys: 'start_day', 'end_day', 'start_hour', 'end_hour',
        'start_minute', 'end_minute'.
        """
        if self.repository.session.in_transaction():  # commit the current transaction if there is one
            self.repository.session.commit()

        with self.repository.session.begin():
            calendar = Calendar()
            for interval in intervals:
                calendar.intervals.append(
                    CalendarInterval(
                        start_day=interval["start_day"],
                        end_day=interval["end_day"],
                        start_hour=interval["start_hour"],
                        end_hour=interval["end_hour"],
                        start_minute=interval.get("start_minute") or 0,
                        end_minute=interval.get("end_minute") or 0,
                    )
                )
            self.repository.session.add(calendar)
        return calendar

    def get_calendar(self, calendar_id: int) -> Calendar:
        """Get a calendar."""
        return self.repository.calendar.get(calendar_id)

    def delete_calendar(self, calendar_id: int):
        """Delete a calendar."""
        self.repository.calendar.delete(calendar_id)

    def create_case_arrival(self, model_id: int, calendar_id: int, distribution_id: int) -> CaseArrival:
        """Create a case arrival."""
        model = self.repository.simulation_model.get(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        calendar = self.repository.calendar.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        distribution = self.repository.distribution.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        return self.repository.case_arrival.create(
            model_id=model_id, calendar_id=calendar_id, distribution_id=distribution_id
        )

    def delete_case_arrival(self, case_arrival_id: int):
        """Delete a case arrival."""
        self.repository.case_arrival.delete(case_arrival_id)

    def create_activity(self, name: str, bpmn_id: str, resource_id: int) -> Activity:
        return self.repository.activity.create(bpmn_id=bpmn_id, name=name, resource_id=resource_id)

    def get_activity(self, activity_id: int) -> Activity:
        """Get an activity."""
        return self.repository.activity.get(activity_id)

    def delete_activity(self, activity_id: int):
        """Delete an activity."""
        self.repository.activity.delete(activity_id)

    def create_resource(
        self,
        bpmn_id: str,
        name: str,
        amount: int,
        cost_per_hour: float,
        calendar_id: int,
    ) -> Resource:
        calendar = self.repository.calendar.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        return self.repository.resource.create(
            bpmn_id=bpmn_id,
            name=name,
            amount=amount,
            cost_per_hour=cost_per_hour,
            calendar_id=calendar_id,
        )

    def create_resource_with_activity_distributions(
        self,
        bpmn_id: str,
        name: str,
        amount: int,
        cost_per_hour: float,
        calendar_id: int,
        activity_distributions: list[dict],
    ) -> Resource:
        """Create a resource with a list of activity distributions. Besides the resource, the function creates
        the activities and their distributions.

        Activity distributions must be a list of dictionaries with keys: 'activity_name', 'distribution'.

        Distribution must be a dictionary with keys: 'name', 'parameters'.
        Distribution parameters must be a list of dictionaries with keys: 'name', 'value'.
        See create_distribution_with_parameters for details.
        """
        calendar = self.repository.calendar.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        resource = self.repository.resource.create(
            bpmn_id=bpmn_id,
            name=name,
            amount=amount,
            cost_per_hour=cost_per_hour,
            calendar_id=calendar_id,
        )
        for activity_distribution in activity_distributions:
            activity = self.create_activity(
                name=activity_distribution["activity_name"],
                bpmn_id=activity_distribution["activity_bpmn_id"],
                resource_id=resource.id,
            )
            distribution = self.create_distribution_with_parameters(
                name=activity_distribution["distribution"]["name"],
                parameters=activity_distribution["distribution"]["parameters"],
            )
            self.create_activity_resource_distribution(
                activity_id=activity.id,
                resource_id=resource.id,
                distribution_id=distribution.id,
            )
        return resource

    def delete_resource(self, resource_id: int):
        """Delete a resource."""
        self.repository.resource.delete(resource_id)

    def create_activity_resource_distribution(
        self, activity_id: int, resource_id: int, distribution_id: int
    ) -> ActivityResourceDistribution:
        """Create an activity resource distribution."""
        activity = self.repository.activity.get(activity_id)
        if not activity:
            raise ValueError(f"Activity with ID {activity_id} not found.")
        resource = self.repository.resource.get(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID {resource_id} not found.")
        distribution = self.repository.distribution.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        return self.repository.activity_resource_distribution.create(
            activity_id=activity_id,
            resource_id=resource_id,
            distribution_id=distribution_id,
        )

    def delete_activity_resource_distribution(self, activity_distribution_id: int):
        """Delete an activity resource distribution."""
        self.repository.activity_resource_distribution.delete(activity_distribution_id)

    def create_resource_profile_with_resources(
        self, model_id: int, name: str, resources: list[dict]
    ) -> ResourceProfile:
        """Create a resource profile with a list of resources.
        Resources must be a list of dictionaries with keys: 'bpmn_id', 'name', 'amount', 'cost_per_hour', 'calendar_id',
        'activity_distributions'.
        See create_resource_with_activity_distributions for details.

        Activity distributions must be a list of dictionaries with keys: 'activity_name', 'activity_bpmn_id',
        'distribution'.

        Distribution must be a dictionary with keys: 'name', 'parameters'.
        Distribution parameters must be a list of dictionaries with keys: 'name', 'value'.
        See create_distribution_with_parameters for details.
        """
        profile = self.repository.resource_profile.create(name=name, model_id=model_id)
        for resource_data in resources:
            resource = self.create_resource_with_activity_distributions(
                bpmn_id=resource_data["bpmn_id"],
                name=resource_data["name"],
                amount=resource_data.get("amount") or 0,
                cost_per_hour=resource_data.get("cost_per_hour") or 0,
                calendar_id=resource_data["calendar_id"],
                activity_distributions=resource_data["activity_distributions"],
            )
            resource.profile_id = profile.id
            self.repository.session.add(resource)
        return profile
