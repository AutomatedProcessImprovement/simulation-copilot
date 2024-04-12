from sqlalchemy_schemadisplay import create_schema_graph

from simulation_copilot.database import create_tables
from simulation_copilot.database import engine, in_memory
from simulation_copilot.prosimos_relational_model import Base

if __name__ == "__main__":
    if in_memory:
        create_tables(engine)
    metadata = Base.metadata
    graph = create_schema_graph(engine=engine, metadata=metadata, rankdir="BT")
    graph.write_png("schema.png")
