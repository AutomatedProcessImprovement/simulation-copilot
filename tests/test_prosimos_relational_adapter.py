import os
import unittest

from simulation_copilot.database import create_tables, engine, session
from simulation_copilot.prosimos_relational_adapter import query_simulation_model
from simulation_copilot.prosimos_relational_repository import ProsimosRelationalRepository


class TestProsimosRelationalAdapter(unittest.TestCase):
    repository: ProsimosRelationalRepository

    @classmethod
    def setUpClass(cls):
        os.environ["DATABASE_URL"] = "sqlite:///:memory:"
        create_tables(engine)

    def setUp(self):
        self.repository = ProsimosRelationalRepository(session)

    def test_query_simulation_model_not_found(self):
        with self.assertRaises(ValueError):
            _ = query_simulation_model(session, 1)

    def test_query_simulation_model(self):
        sql_model = self.repository.simulation_model.create()

        model = query_simulation_model(session, sql_model.id)
        self.assertIsNotNone(model)

        self.repository.simulation_model.delete(sql_model.id)


if __name__ == "__main__":
    unittest.main()
