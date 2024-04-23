"""In this script, we use the Anthropic SDK instead of LangChain.
"""

import json
import tempfile
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from prosimos.simulation_engine import run_simulation

from simulation_copilot.anthropic import Conversation
from simulation_copilot.anthropic.conversation import Claude3
from simulation_copilot.database import (
    create_tables,
    tables_schema,
    get_session,
)
from simulation_copilot.prosimos_relational_service import ProsimosRelationalService
from simulation_copilot.prosimos_to_relational_adapter import create_simulation_model_from_pix
from simulation_copilot.relational_to_prosimos_adapter import create_simulation_model_from_relational_data
from simulation_copilot.tools.prosimos_relational_tools import (
    create_simulation_model,
    get_simulation_model,
    change_resource_amount,
    add_resource_to_profile,
    remove_resource_from_profile_by_id,
    create_calendar_with_intervals,
    create_distribution,
    add_case_arrival,
    get_resource_id_by_name,
)

tools = [
    create_simulation_model,
    get_simulation_model,
    change_resource_amount,
    get_resource_id_by_name,
    add_resource_to_profile,
    remove_resource_from_profile_by_id,
    create_calendar_with_intervals,
    create_distribution,
    add_case_arrival,
]

model_path = Path(__file__).parent.parent.parent.parent / "tests/test_data/PurchasingExample/simulation.json"
process_path = Path(__file__).parent.parent.parent.parent / "tests/test_data/PurchasingExample/process.bpmn"


def compose_instructions(simulation_model_id: int) -> str:
    """
    System instructions for the assistant.
    """
    # pylint: disable=line-too-long
    context = f"""You are an assistant who helps with preparing of a business process simulation model.
The model is represented by a set of tables in a SQL database. Reuse calendars whenever possible.

Note: In activity distributions, the distribution name is the name of the distribution and the parameters is a list of
parameters for this specific distribution. The name and number of distribution parameters depend on the distribution.
Note: If you are lacking some information, query the database using the provided tools. Always try to query the lacking
information from the database first before asking the user.

Below is the SQL schema for simulation model tables;

{tables_schema()}

You don't need to query the database directly, but you can use the provided tools to interact with the database.
Note: Use one tool at a time, then, wait for a new request to adjust input parameters for the next tool call if needed.

The initial simulation model ID is {simulation_model_id}. All further user requests will be based on this model.
"""
    return context


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


def run_prosimos(model_id: int) -> str:
    """
    Runs the simulation with the given model ID. Returns the simulation performance report.
    """
    with get_session() as session:
        bps_model = create_simulation_model_from_relational_data(session, model_id)
        simulation_attributes = bps_model.to_prosimos_format(process_model=process_path)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as f:
            # save the simulation model to a temporary file
            json.dump(simulation_attributes, f)
            f.flush()  # otherwise, the file content is truncated
            simulation_report_path = Path(f.name).with_suffix(".csv")

            # run simulation
            run_simulation(
                bpmn_path=process_path,
                json_path=f.name,
                total_cases=100,
                stat_out_path=simulation_report_path,
            )
            with open(simulation_report_path, "r", encoding="utf-8") as report_file:
                report = report_file.read()
    return report


def load_initial_simulation_model() -> int:
    """
    Loads the initial simulation model from a JSON file. Returns the ID of the relational model.
    """
    with model_path.open("r") as f:
        model = json.load(f)
    with get_session() as session:
        relational_model = create_simulation_model_from_pix(session, model, process_path)
    return relational_model.id


def main():
    # pylint: disable=missing-function-docstring,line-too-long

    load_dotenv()
    create_tables()
    simulation_model_id = load_initial_simulation_model()
    initial_performance = run_prosimos(simulation_model_id)

    try:
        conversation = Conversation(
            model=Claude3.OPUS.value,
            tools=tools,
            system_instructions=compose_instructions(simulation_model_id),
        )
        conversation.run("""What if we increase the amount of resource named 'Sean Manney' to 10?""")
    except anthropic.BadRequestError as e:
        print(e)

    updated_performance = run_prosimos(simulation_model_id)
    print(f"\nInitial performance\n{initial_performance}")
    print(f"\nUpdated performance\n{updated_performance}")


if __name__ == "__main__":
    load_dotenv()
    main()

# pylint: disable=fixme
# TODO: handle error in tools
# TODO: add UI
# TODO: add another agent who runs the simulation and compares initial simulation model with the updated one
