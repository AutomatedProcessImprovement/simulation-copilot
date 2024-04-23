# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
# pylint: disable=R0801
import json
import os
import tempfile
import unittest
from pathlib import Path

from prosimos.simulation_engine import run_simulation

from simulation_copilot.database import create_tables, Session
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.prosimos_to_relational_adapter import create_simulation_model_from_pix
from simulation_copilot.relational_to_prosimos_adapter import create_simulation_model_from_relational_data


class TestRelationalToProsimosSimulation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables()

    def setUp(self):
        self.session = Session()
        self.service = ProsimosRelationalService(self.session)

    def tearDown(self):
        self.session.close()

    def test_simulation_run_ok(self):
        # load a proper simulation model
        model_path = Path(__file__).parent / "test_data/PurchasingExample/simulation.json"
        process_path = Path(__file__).parent / "test_data/PurchasingExample/process.bpmn"
        with model_path.open("r") as f:
            model = json.load(f)
        relational_model = create_simulation_model_from_pix(self.session, model, process_path)
        bps_model = create_simulation_model_from_relational_data(self.session, relational_model.id)
        simulation_attributes = bps_model.to_prosimos_format(process_model=process_path)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            # save the simulation model to a temporary file
            json.dump(simulation_attributes, f)
            f.flush()  # otherwise, the file content is truncated
            simulation_report_path = Path(f.name).with_suffix(".csv")

            # run Prosimos
            run_simulation(
                bpmn_path=process_path, json_path=f.name, total_cases=100, stat_out_path=simulation_report_path
            )

            # check if the simulation report was generated
            self.assertTrue(simulation_report_path.exists())

            # cleanup
            os.remove(simulation_report_path)
