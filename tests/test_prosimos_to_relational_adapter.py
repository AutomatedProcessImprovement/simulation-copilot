# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=R0801
import json
import os
import unittest
from pathlib import Path

from simulation_copilot.database import create_tables, Session
from simulation_copilot.prosimos_relational_model import SimulationModel
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.prosimos_to_relational_adapter import create_simulation_model_from_pix


class TestProsimosToRelationalAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables()

    def setUp(self):
        self.session = Session()
        self.service = ProsimosRelationalService(self.session)

    def tearDown(self):
        self.session.close()

    def test_create_simulation_model_ok(self):
        model_path = Path(__file__).parent / "test_data/PurchasingExample/simulation.json"
        process_path = Path(__file__).parent / "test_data/PurchasingExample/process.bpmn"
        with model_path.open("r") as f:
            model = json.load(f)

        relational_model = create_simulation_model_from_pix(self.session, model, process_path)

        self.assertIsNotNone(relational_model)
        self.assertTrue(isinstance(relational_model, SimulationModel))
        self.assertTrue(len(relational_model.resource_profiles) == len(model["resource_profiles"]))
        self.assertTrue(len(relational_model.gateways) == len(model["gateway_branching_probabilities"]))
        self.assertTrue(relational_model.case_arrival is not None)
        self.assertEqual(
            relational_model.case_arrival.inter_arrival_distribution.name,
            model["arrival_time_distribution"]["distribution_name"],
        )
        self.assertEqual(
            len(relational_model.case_arrival.inter_arrival_distribution.parameters),
            len(model["arrival_time_distribution"]["distribution_params"]),
        )


if __name__ == "__main__":
    unittest.main()
