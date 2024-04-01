import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from simulation_copilot.tables import Base

# Create the database engine
engine = sa.create_engine("sqlite:///simulation_model.db")

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


def save_table_schemas(table_names, path):
    with open(path, "w") as f:
        for table_name in table_names:
            f.write(
                sa.schema.CreateTable(Base.metadata.tables[table_name])
                .compile(engine)
                .string
            )


if __name__ == "__main__":
    # Create the tables
    Base.metadata.create_all(engine)

    # Write SQL schemas to file. LLM uses it to understand the database structure.
    save_table_schemas(
        [
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
        ],
        "simulation_copilot/schemas.sql",
    )
