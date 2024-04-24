"""Helpers for the CLI."""
from simulation_copilot.database import get_session
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.relational_to_prosimos_adapter import create_simulation_model_from_relational_data


def print_all_simulation_models():
    """Converts relational simulation models to BPSModel and prints out to stdout."""
    session = get_session()
    service = ProsimosRelationalService(session)
    sql_models = service.get_all_simulation_models()
    for model in sql_models:
        pix_model = create_simulation_model_from_relational_data(session, model.id)
        print("\nPIX simulation model dump:")
        print(f"Model ID: {model.id}")
        print(pix_model)


def print_simulation_model(model_id: int):
    """Converts a relational simulation model to BPSModel and prints out to stdout."""
    with get_session() as session:
        bps_model = create_simulation_model_from_relational_data(session, model_id)
        print("\nPIX simulation model dump:")
        print(f"Model ID: {model_id}")
        print(bps_model)
