import os
import unittest

from simulation_copilot.database import create_tables, engine, session
from simulation_copilot.prosimos_relational_repository import ProsimosRelationalRepository


class TestProsimosRelationalRepository(unittest.TestCase):
    repository: ProsimosRelationalRepository

    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables(engine)

    def setUp(self):
        self.repository = ProsimosRelationalRepository(session)

    def test_create_simulation_model(self):
        model = self.repository.simulation_model.create()
        self.assertIsNotNone(model)

    def test_create_gateway(self):
        model = self.repository.simulation_model.create()
        gateway = self.repository.gateway.create(model.id, "bpmn_id")
        self.assertIsNotNone(gateway)
        self.assertEqual(gateway.simulation_model_id, model.id)

    def test_add_sequence_flow(self):
        model = self.repository.simulation_model.create()
        gateway = self.repository.gateway.create(model.id, "bpmn_id")
        flow = self.repository.gateway.add_sequence_flow(gateway.id, "bpmn_id", 0.5)
        self.assertIsNotNone(flow)
        self.assertEqual(flow.source_gateway_id, gateway.id)
        self.assertEqual(flow.probability, 0.5)
        self.assertEqual(gateway.outgoing_sequence_flows[0], flow)

    def test_create_distribution(self):
        distribution = self.repository.distribution.create("normal")
        self.assertIsNotNone(distribution)
        self.assertEqual(distribution.name, "normal")

    def test_create_distribution_parameter(self):
        distribution = self.repository.distribution.create("normal")
        parameter = self.repository.distribution.add_parameter(distribution.id, "mean", 1)
        self.assertIsNotNone(parameter)
        self.assertEqual(parameter.distribution_id, distribution.id)
        self.assertEqual(parameter.name, "mean")
        self.assertEqual(parameter.value, 1)
        self.assertEqual(distribution.parameters[0], parameter)

    def test_create_calendar(self):
        calendar = self.repository.calendar.create()
        self.assertIsNotNone(calendar)

    def test_add_calendar_interval(self):
        calendar = self.repository.calendar.create()
        interval = self.repository.calendar.add_interval(
            calendar.id, start_day="Monday", end_day="Tuesday", start_hour=9, end_hour=17, start_minute=0, end_minute=0
        )
        self.assertIsNotNone(interval)
        self.assertEqual(interval.calendar_id, calendar.id)
        self.assertEqual(interval.start_day, "Monday")
        self.assertEqual(interval.end_day, "Tuesday")
        self.assertEqual(interval.start_hour, 9)
        self.assertEqual(interval.end_hour, 17)
        self.assertEqual(interval.start_minute, 0)
        self.assertEqual(interval.end_minute, 0)
        self.assertEqual(calendar.intervals[0], interval)

    def test_create_case_arrival(self):
        case_arrival = self.repository.case_arrival.create(calendar_id=1, distribution_id=1, model_id=1)
        self.assertIsNotNone(case_arrival)
        self.assertIsNotNone(case_arrival.id)
        self.assertEqual(case_arrival.calendar_id, 1)
        self.assertEqual(case_arrival.inter_arrival_distribution_id, 1)
        self.assertEqual(case_arrival.simulation_model_id, 1)

    def test_create_activity(self):
        activity = self.repository.activity.create(name="activity_1", bpmn_id="bpmn_id", resource_id=1)
        self.assertIsNotNone(activity)
        self.assertEqual(activity.name, "activity_1")
        self.assertEqual(activity.bpmn_id, "bpmn_id")
        self.assertEqual(activity.resource_id, 1)

    def test_create_activity_resource_distribution(self):
        activity_distribution = self.repository.activity_resource_distribution.create(
            activity_id=1, resource_id=1, distribution_id=1
        )
        self.assertIsNotNone(activity_distribution)
        self.assertEqual(activity_distribution.activity_id, 1)
        self.assertEqual(activity_distribution.distribution_id, 1)

    def test_create_resource_profile(self):
        resource_profile = self.repository.resource_profile.create(name="profile_1", model_id=1)
        self.assertIsNotNone(resource_profile)
        self.assertEqual(resource_profile.name, "profile_1")
        self.assertEqual(resource_profile.simulation_model_id, 1)

    def test_add_resource(self):
        resource_profile = self.repository.resource_profile.create(name="profile_1", model_id=1)
        resource = self.repository.resource_profile.add_resource(
            profile_id=resource_profile.id,
            name="resource_1",
            amount=5,
            cost_per_hour=10.0,
            calendar_id=1,
            bpmn_id="bpmn_id",
        )
        self.assertIsNotNone(resource)
        self.assertEqual(resource.name, "resource_1")
        self.assertEqual(resource.amount, 5)
        self.assertEqual(resource.cost_per_hour, 10.0)
        self.assertEqual(resource.calendar_id, 1)
        self.assertEqual(resource.profile_id, 1)
        self.assertEqual(resource_profile.resources[0], resource)


if __name__ == "__main__":
    unittest.main()
