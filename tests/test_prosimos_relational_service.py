import os
import unittest

from simulation_copilot.database import Session, create_tables, engine
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService


class TestProsimosRelationalService(unittest.TestCase):
    service: ProsimosRelationalService

    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables(engine)

    def setUp(self):
        self.session = Session()
        self.service = ProsimosRelationalService(self.session)

    def tearDown(self):
        self.session.close()

    def test_create_simulation_model_ok(self):
        model = self.service.create_simulation_model()
        self.assertIsNotNone(model)

        self.service.delete_simulation_model(model.id)

    def test_add_new_gateway_with_sequence_flow_ok(self):
        model = self.service.create_simulation_model()
        gateway = self.service.create_gateway_with_sequence_flows(
            model.id, "bpmn_id", [{"bpmn_id": "flow_id", "probability": 0.5}]
        )
        self.assertIsNotNone(gateway)
        self.assertEqual(gateway.bpmn_id, "bpmn_id")
        self.assertEqual(gateway.outgoing_sequence_flows[0].bpmn_id, "flow_id")
        self.assertEqual(gateway.outgoing_sequence_flows[0].probability, 0.5)
        self.assertEqual(len(gateway.outgoing_sequence_flows), 1)

        self.service.delete_simulation_model(model.id)

    def test_add_new_gateway_with_sequence_flow_error(self):
        with self.assertRaises(ValueError):
            self.service.create_gateway_with_sequence_flows(1, "bpmn_id", [{"bpmn_id": "flow_id", "probability": 0.5}])

    def test_create_distribution_with_parameters_ok(self):
        distribution = self.service.create_distribution_with_parameters("normal", [{"name": "mean", "value": 1}])
        self.assertIsNotNone(distribution)
        self.assertEqual(distribution.name, "normal")
        self.assertEqual(distribution.parameters[0].name, "mean")
        self.assertEqual(distribution.parameters[0].value, 1)

        self.service.delete_distribution(distribution.id)

    def test_create_distribution_with_parameters_error(self):
        with self.assertRaises(KeyError):
            self.service.create_distribution_with_parameters("normal", [{"value": 1}])

    def test_create_calendar_with_intervals_ok(self):
        calendar = self.service.create_calendar_with_intervals(
            [
                {
                    "start_day": "Monday",
                    "end_day": "Tuesday",
                    "start_hour": 0,
                    "end_hour": 1,
                    "start_minute": 0,
                    "end_minute": 0,
                }
            ]
        )
        self.assertIsNotNone(calendar)
        self.assertEqual(len(calendar.intervals), 1)
        self.assertEqual(calendar.intervals[0].start_day, "Monday")
        self.assertEqual(calendar.intervals[0].end_day, "Tuesday")
        self.assertEqual(calendar.intervals[0].start_hour, 0)
        self.assertEqual(calendar.intervals[0].end_hour, 1)
        self.assertEqual(calendar.intervals[0].start_minute, 0)
        self.assertEqual(calendar.intervals[0].end_minute, 0)

        self.service.delete_calendar(calendar.id)

    def test_create_calendar_with_intervals_not_full_ok(self):
        calendar = self.service.create_calendar_with_intervals(
            [
                {
                    "start_day": "Monday",
                    "end_day": "Tuesday",
                    "start_hour": 0,
                    "end_hour": 1,
                }
            ]
        )
        self.assertIsNotNone(calendar)
        self.assertEqual(len(calendar.intervals), 1)
        self.assertEqual(calendar.intervals[0].start_day, "Monday")
        self.assertEqual(calendar.intervals[0].end_day, "Tuesday")
        self.assertEqual(calendar.intervals[0].start_hour, 0)
        self.assertEqual(calendar.intervals[0].end_hour, 1)
        self.assertEqual(calendar.intervals[0].start_minute, 0)
        self.assertEqual(calendar.intervals[0].end_minute, 0)

        self.service.delete_calendar(calendar.id)

    def test_create_calendar_with_intervals_error(self):
        with self.assertRaises(KeyError):
            self.service.create_calendar_with_intervals(
                [{"start_day": "Monday", "end_day": "Tuesday", "start_hour": 0}]
            )

    def test_create_case_arrival_ok(self):
        model = self.service.create_simulation_model()
        calendar = self.service.create_calendar_with_intervals(
            [
                {
                    "start_day": "Monday",
                    "end_day": "Tuesday",
                    "start_hour": 0,
                    "end_hour": 1,
                    "start_minute": 0,
                    "end_minute": 0,
                }
            ]
        )
        distribution = self.service.create_distribution_with_parameters("normal", [{"name": "mean", "value": 1}])
        case_arrival = self.service.create_case_arrival(model.id, calendar.id, distribution.id)
        self.assertIsNotNone(case_arrival)
        self.assertEqual(case_arrival.calendar_id, calendar.id)
        self.assertEqual(case_arrival.inter_arrival_distribution_id, distribution.id)
        self.assertEqual(case_arrival.simulation_model_id, model.id)

        self.service.delete_calendar(calendar.id)
        self.service.delete_distribution(distribution.id)
        self.service.delete_case_arrival(case_arrival.id)
        self.service.delete_simulation_model(model.id)

    def test_create_case_arrival_errors(self):
        with self.assertRaises(ValueError):
            self.service.create_case_arrival(1, 1, 1)

    def test_create_resource_ok(self):
        calendar = self.service.create_calendar_with_intervals(
            [
                {
                    "start_day": "Monday",
                    "end_day": "Tuesday",
                    "start_hour": 0,
                    "end_hour": 1,
                    "start_minute": 0,
                    "end_minute": 0,
                }
            ]
        )
        resource = self.service.create_resource(
            name="A",
            bpmn_id="bpmn_id",
            amount=1,
            cost_per_hour=1,
            calendar_id=calendar.id,
        )
        self.assertIsNotNone(resource)
        self.assertEqual(resource.name, "A")
        self.assertEqual(resource.bpmn_id, "bpmn_id")
        self.assertEqual(resource.amount, 1)
        self.assertEqual(resource.cost_per_hour, 1)
        self.assertEqual(resource.calendar_id, calendar.id)
        self.assertIsNone(resource.profile_id)
        self.assertEqual(resource.assigned_activities, [])

        self.service.delete_resource(resource.id)
        self.service.delete_calendar(calendar.id)

    def test_create_resource_error(self):
        with self.assertRaises(ValueError):
            self.service.create_resource(name="A", bpmn_id="bpmn_id", amount=1, cost_per_hour=1, calendar_id=1)

    def test_create_activity_resource_distribution_ok(self):
        calendar = self.service.create_calendar_with_intervals(
            intervals=[{"start_day": "Monday", "end_day": "Tuesday", "start_hour": 0, "end_hour": 1}]
        )
        resource = self.service.create_resource(
            name="A", bpmn_id="bpmn_id", amount=1, cost_per_hour=1, calendar_id=calendar.id
        )
        activity = self.service.create_activity(bpmn_id="bpmn_id", resource_id=resource.id, name="activity_1")
        distribution = self.service.create_distribution_with_parameters("normal", [{"name": "mean", "value": 1}])
        activity_distribution = self.service.create_activity_resource_distribution(
            activity_id=activity.id,
            resource_id=resource.id,
            distribution_id=distribution.id,
        )
        self.assertIsNotNone(activity_distribution)
        self.assertEqual(activity_distribution.activity_id, activity.id)
        self.assertEqual(activity_distribution.resource_id, resource.id)
        self.assertEqual(activity_distribution.distribution_id, distribution.id)

        self.service.delete_calendar(calendar.id)
        self.service.delete_activity(activity.id)
        self.service.delete_resource(resource.id)
        self.service.delete_distribution(distribution.id)
        self.service.delete_activity_resource_distribution(activity_distribution.id)

    def test_create_activity_resource_distribution_error(self):
        with self.assertRaises(ValueError):
            self.service.create_activity_resource_distribution(1, 1, 1)
