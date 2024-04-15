from sqlalchemy.orm import Session

from simulation_copilot.prosimos_relational_model import (
    Calendar,
    CalendarInterval,
    Gateway,
    SequenceFlow,
)
from simulation_copilot.prosimos_relational_repository import (
    ProsimosRelationalRepository,
)


class ProsimosRelationalService(ProsimosRelationalRepository):
    """Service for the Prosimos relational database."""

    def __init__(self, session: Session):
        super().__init__(session)

    def create_simulation_model(self):
        """Create a simulation model."""
        return self.simulation_model.create()

    def delete_simulation_model(self, model_id: int):
        """Delete a simulation model."""
        self.simulation_model.delete(model_id)

    def add_new_gateway_with_sequence_flows(self, model_id: int, gateway_bpmn_id: str, flows: list[dict]):
        """Create a gateway with a list of sequence flows.
        Flows must be a list of dictionaries with keys 'bpmn_id' and 'probability'."""
        model = self.simulation_model.get(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")

        if self.session.in_transaction():  # commit the current transaction if there is one
            self.session.commit()

        with self.session.begin():
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
            self.session.add(gateway)
            self.session.refresh(model)
        return gateway

    def create_distribution_with_parameters(self, name: str, parameters: list[dict]):
        """Create a distribution with a list of parameters.
        Parameters must be a list of dictionaries with keys 'name' and 'value'.
        """
        distribution = self.distribution.create(name)
        self.distribution.add_parameters(distribution_id=distribution.id, parameters=parameters)
        return distribution

    def delete_distribution(self, distribution_id: int):
        """Delete a distribution."""
        self.distribution.delete(distribution_id)

    def create_calendar_with_intervals(self, intervals: list[dict]):
        """Create a calendar with a list of intervals.
        Intervals must be a list of dictionaries with keys: 'start_day', 'end_day', 'start_hour', 'end_hour',
        'start_minute', 'end_minute'.
        """
        if self.session.in_transaction():  # commit the current transaction if there is one
            self.session.commit()

        with self.session.begin():
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
            self.session.add(calendar)
        return calendar

    def delete_calendar(self, calendar_id: int):
        """Delete a calendar."""
        self.calendar.delete(calendar_id)

    def create_case_arrival(self, model_id: int, calendar_id: int, distribution_id: int):
        """Create a case arrival."""
        model = self.simulation_model.get(model_id)
        if not model:
            raise ValueError(f"Model with ID {model_id} not found.")
        calendar = self.calendar.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        distribution = self.distribution.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        return self.case_arrival.create(model_id=model_id, calendar_id=calendar_id, distribution_id=distribution_id)

    def delete_case_arrival(self, case_arrival_id: int):
        """Delete a case arrival."""
        self.case_arrival.delete(case_arrival_id)

    def create_activity(self, name: str, bpmn_id: str, resource_id: int):
        return self.activity.create(bpmn_id=bpmn_id, name=name, resource_id=resource_id)

    def delete_activity(self, activity_id: int):
        """Delete an activity."""
        self.activity.delete(activity_id)

    def create_resource(
        self,
        bpmn_id: str,
        name: str,
        amount: int,
        cost_per_hour: float,
        calendar_id: int,
    ):
        calendar = self.calendar.get(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar with ID {calendar_id} not found.")
        return self.resource.create(
            bpmn_id=bpmn_id,
            name=name,
            amount=amount,
            cost_per_hour=cost_per_hour,
            calendar_id=calendar_id,
        )

    def delete_resource(self, resource_id: int):
        """Delete a resource."""
        self.resource.delete(resource_id)

    def create_activity_resource_distribution(self, activity_id: int, resource_id: int, distribution_id: int):
        """Create an activity resource distribution."""
        activity = self.activity.get(activity_id)
        if not activity:
            raise ValueError(f"Activity with ID {activity_id} not found.")
        resource = self.resource.get(resource_id)
        if not resource:
            raise ValueError(f"Resource with ID {resource_id} not found.")
        distribution = self.distribution.get(distribution_id)
        if not distribution:
            raise ValueError(f"Distribution with ID {distribution_id} not found.")
        return self.activity_resource_distribution.create(
            activity_id=activity_id,
            resource_id=resource_id,
            distribution_id=distribution_id,
        )

    def delete_activity_resource_distribution(self, activity_distribution_id: int):
        """Delete an activity resource distribution."""
        self.activity_resource_distribution.delete(activity_distribution_id)

    def create_resource_profile_with_resources(self, model_id: int, name: str, resources: list[dict]):
        """Create a resource profile with a list of resources.
        Resources must be a list of dictionaries with keys: 'bpmn_id', 'name', 'amount', 'cost_per_hour', 'calendar_id'.
        """
        profile = self.resource_profile.create(name=name, model_id=model_id)
        self.resource_profile.add_resources(profile_id=profile.id, resources=resources)
        return profile
