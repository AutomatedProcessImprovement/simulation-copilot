import os
import unittest

from simulation_copilot.database import create_tables, engine, Session
from simulation_copilot.prosimos_relational_adapter import query_simulation_model
from simulation_copilot.prosimos_relational_repository import ProsimosRelationalRepository


class TestProsimosRelationalAdapter(unittest.TestCase):
    repository: ProsimosRelationalRepository

    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables(engine)

    def setUp(self):
        self.session = Session()
        self.repository = ProsimosRelationalRepository(self.session)

    def tearDown(self):
        self.session.close()

    def test_query_simulation_model_not_found(self):
        with self.assertRaises(ValueError):
            _ = query_simulation_model(self.session, 1)

    def test_query_simulation_model(self):
        sql_model = self.repository.simulation_model.create()
        gateway = self.repository.gateway.create(model_id=sql_model.id, bpmn_id="bpmn_id")
        self.repository.gateway.add_sequence_flow(gateway_id=gateway.id, bpmn_id="bpmn_id_2", probability=0.9)

        model = query_simulation_model(self.session, sql_model.id)
        self.assertIsNotNone(model)
        self.assertTrue(len(model.gateway_probabilities) > 0)

        self.repository.simulation_model.delete(sql_model.id)


if __name__ == "__main__":
    unittest.main()
