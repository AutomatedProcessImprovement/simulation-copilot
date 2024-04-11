from pathlib import Path

import sqlalchemy as sa

from simulation_copilot.sql_approach.db import engine
from simulation_copilot.sql_approach.tables import Base

SQL_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

table_names = [
    "calendar_intervals",
    "calendars",
    "activities",
    "distribution_parameters",
    "activity_distributions",
    "resources",
    "resource_profiles",
    "sequence_flows",
    "gateways",
    "simulation_models",
]


def tables_schema(tables=None):
    if tables is None:
        tables = table_names

    output = ""
    for table in tables:
        output += sa.schema.CreateTable(Base.metadata.tables[table]).compile(engine).string

    return output


def save_tables_schema(table_names, path):
    with open(path, "w") as f:
        f.write(tables_schema(table_names))


def create_tables(engine):
    Base.metadata.create_all(engine)


if __name__ == "__main__":
    create_tables(engine)
    save_tables_schema(table_names, SQL_SCHEMA_PATH)