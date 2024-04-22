# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import os
import unittest

from simulation_copilot.database import create_tables, Session
from simulation_copilot.prosimos_relational_repository import (
    ProsimosRelationalRepository,
)


# NOTE: perhaps, testing Repository isn't necessary if we have tested the Service


class TestProsimosRelationalRepository(unittest.TestCase):
    repository: ProsimosRelationalRepository

    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables()

    def setUp(self):
        self.session = Session()
        self.repository = ProsimosRelationalRepository(self.session)

    def tearDown(self):
        # delete all data from the tables
        self.repository.simulation_model.delete_all()
        self.repository.gateway.delete_all()
        self.repository.distribution.delete_all()
        self.repository.calendar.delete_all()
        self.repository.case_arrival.delete_all()
        self.repository.activity.delete_all()
        self.repository.activity_resource_distribution.delete_all()
        self.repository.resource_profile.delete_all()
        self.repository.resource.delete_all()
        self.session.close()

    def test_create_simulation_model(self):
        model = self.repository.simulation_model.create()
        self.assertIsNotNone(model)

    def test_delete_simulation_model(self):
        model = self.repository.simulation_model.create()
        gateway = self.repository.gateway.create(model.id, "bpmn_id")
        flow = self.repository.gateway.add_sequence_flow(gateway.id, "bpmn_id", 0.5)

        self.repository.simulation_model.delete(model.id)

        self.assertIsNone(self.repository.simulation_model.get(model.id))
        self.assertIsNone(self.repository.gateway.get(gateway.id))
        self.assertIsNone(self.repository.gateway.get_sequence_flow(flow.id))

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
        calendar = self.repository.calendar.create()
        resource = self.repository.resource.create(
            name="A", bpmn_id="bpmn_id", amount=5, cost_per_hour=10.0, calendar_id=calendar.id
        )
        profile = self.repository.resource_profile.add_resource(profile_id=resource_profile.id, resource_id=resource.id)
        self.assertIsNotNone(resource)
        self.assertEqual(resource.profile_id, resource_profile.id)
        self.assertEqual(resource_profile.resources[0], resource)
        self.assertEqual(profile.resources[0], resource)


if __name__ == "__main__":
    unittest.main()
