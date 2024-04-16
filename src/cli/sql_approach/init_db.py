from pathlib import Path

import sqlalchemy as sa

from simulation_copilot.database import create_tables
from simulation_copilot.database import engine
from simulation_copilot.prosimos_relational_model import Base

SQL_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

table_names = Base.metadata.tables.keys()


def tables_schema():
    output = ""
    for table in Base.metadata.tables.keys():
        output += sa.schema.CreateTable(Base.metadata.tables[table]).compile(engine).string
    return output


def save_tables_schema(path):
    with open(path, "w") as f:
        f.write(tables_schema())


if __name__ == "__main__":
    create_tables(engine)
    save_tables_schema(SQL_SCHEMA_PATH)
