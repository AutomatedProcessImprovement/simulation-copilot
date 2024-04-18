from sqlalchemy_schemadisplay import create_schema_graph

from simulation_copilot.database import _engine, _IN_MEMORY
from simulation_copilot.database import create_tables
from simulation_copilot.prosimos_relational_model import Base

if __name__ == "__main__":
    if _IN_MEMORY:
        create_tables()
    metadata = Base.metadata
    graph = create_schema_graph(engine=_engine, metadata=metadata, rankdir="BT")
    graph.write_png("schema.png")
