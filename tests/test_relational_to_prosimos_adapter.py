# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=R0801
import os
import unittest

from simulation_copilot.database import create_tables, Session
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.relational_to_prosimos_adapter import create_simulation_model_from_relational_data


class TestRelationalToProsimosAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables()

    def setUp(self):
        self.session = Session()
        self.service = ProsimosRelationalService(self.session)

    def tearDown(self):
        self.session.close()

    def test_model_not_found(self):
        with self.assertRaises(ValueError):
            _ = create_simulation_model_from_relational_data(self.session, 1)

    def test_gateways_ok(self):
        sql_model = self.service.create_simulation_model()
        self.service.create_gateway_with_sequence_flows(
            model_id=sql_model.id,
            gateway_bpmn_id="gateway1",
            flows=[
                {"bpmn_id": "flow1", "probability": 0.5},
                {"bpmn_id": "flow2", "probability": 0.5},
            ],
        )

        bps_model = create_simulation_model_from_relational_data(self.session, sql_model.id)

        self.assertIsNotNone(bps_model)
        self.assertTrue(len(bps_model.gateway_probabilities) > 0)

        self.service.delete_simulation_model(sql_model.id)

    def test_case_arrival_ok(self):
        sql_model = self.service.create_simulation_model()
        arrival_calendar = self.service.create_calendar_with_intervals(
            [{"start_day": "Monday", "end_day": "Friday", "start_hour": 8, "end_hour": 17}]
        )
        arrival_distribution = self.service.create_distribution_with_parameters(
            name="exponential",
            parameters=[{"name": "mean", "value": 0.5}, {"name": "min", "value": 0.1}, {"name": "max", "value": 1.0}],
        )
        self.service.create_case_arrival(
            model_id=sql_model.id, calendar_id=arrival_calendar.id, distribution_id=arrival_distribution.id
        )

        bps_model = create_simulation_model_from_relational_data(self.session, sql_model.id)

        self.assertIsNotNone(bps_model)
        self.assertIsNotNone(bps_model.case_arrival_model)
        self.assertIsNotNone(bps_model.case_arrival_model.case_arrival_calendar)
        self.assertIsNotNone(bps_model.case_arrival_model.inter_arrival_times)
        self.assertTrue(len(bps_model.case_arrival_model.inter_arrival_times) > 0)

        self.service.delete_simulation_model(sql_model.id)

    def test_resource_profiles_ok(self):
        sql_model = self.service.create_simulation_model()
        calendar = self.service.create_calendar_with_intervals(
            [{"start_day": "Monday", "end_day": "Friday", "start_hour": 8, "end_hour": 17}]
        )
        self.service.create_resource_profile_with_resources(
            model_id=sql_model.id,
            name="profile1",
            resources=[
                {
                    "name": "resource1",
                    "bpmn_id": "task1",
                    "amount": 1,
                    "calendar_id": calendar.id,
                    "activity_distributions": [
                        {
                            "activity_name": "task1",
                            "activity_bpmn_id": "task1",
                            "distribution": {"name": "fixed", "parameters": [{"name": "mean", "value": 0.5}]},
                        }
                    ],
                },
                {
                    "name": "resource2",
                    "bpmn_id": "task2",
                    "amount": 2,
                    "calendar_id": calendar.id,
                    "activity_distributions": [
                        {
                            "activity_name": "task2",
                            "activity_bpmn_id": "task2",
                            "distribution": {"name": "fixed", "parameters": [{"name": "mean", "value": 0.8}]},
                        }
                    ],
                },
            ],
        )

        bps_model = create_simulation_model_from_relational_data(self.session, sql_model.id)

        self.assertIsNotNone(bps_model)
        self.assertTrue(len(bps_model.resource_model.resource_profiles) == 1)
        self.assertTrue(len(bps_model.resource_model.resource_profiles[0].resources) == 2)
        self.assertTrue(len(bps_model.resource_model.resource_calendars) == 1)
        self.assertTrue(bps_model.resource_model.resource_profiles[0].resources[0].amount == 1)
        self.assertTrue(bps_model.resource_model.resource_profiles[0].resources[1].amount == 2)
        self.assertTrue(len(bps_model.resource_model.activity_resource_distributions) == 2)

        self.service.delete_simulation_model(sql_model.id)

    def test_empty_model_ok(self):
        sql_model = self.service.create_simulation_model()

        bps_model = create_simulation_model_from_relational_data(self.session, sql_model.id)

        self.assertIsNotNone(bps_model)
        self.assertIsNone(bps_model.resource_model)
        self.assertIsNone(bps_model.case_arrival_model)
        self.assertIsNone(bps_model.gateway_probabilities)

        self.service.delete_simulation_model(sql_model.id)


if __name__ == "__main__":
    unittest.main()
