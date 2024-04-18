from pathlib import Path

from simulation_copilot.database import tables_schema, create_tables
from simulation_copilot.prosimos_relational_model import Base

SQL_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

table_names = Base.metadata.tables.keys()


def save_tables_schema(path):
    with open(path, "w") as f:
        f.write(tables_schema())


if __name__ == "__main__":
    create_tables()
    save_tables_schema(SQL_SCHEMA_PATH)
