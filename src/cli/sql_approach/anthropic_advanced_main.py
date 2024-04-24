"""In this script, we use the Anthropic SDK instead of LangChain.
"""

import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from simulation_copilot.anthropic import Conversation
from simulation_copilot.anthropic.conversation import Claude3
from simulation_copilot.database import create_tables, tables_schema, get_session
from simulation_copilot.prosimos_to_relational_adapter import (
    create_simulation_model_from_pix,
)
from simulation_copilot.prosimos_utils import (
    run_prosimos,
    get_resource_utilization_and_overall_statistics,
)
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
    get_baseline_performance_report,
    generate_performance_report,
    set_baseline_performance_report,
    set_process_path,
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
    get_baseline_performance_report,
    generate_performance_report,
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

After you finished implementing the changes that the user has asked, at the end of the user session,
generate a new performance report for the updated simulation model. Then, analyze the baseline performance
with the updated performance and return a summary to the user if the change was effective or not.
"""
    return context


def load_initial_simulation_model() -> int:
    """
    Loads the initial simulation model from a JSON file. Returns the ID of the relational model.
    """
    with model_path.open("r") as f:
        model = json.load(f)
    with get_session() as session:
        relational_model = create_simulation_model_from_pix(session, model, process_path)
    return relational_model.id


# pylint: disable=missing-function-docstring
def main():
    load_dotenv()
    create_tables()
    # import initial simulation model
    simulation_model_id = load_initial_simulation_model()
    baseline_performance = run_prosimos(simulation_model_id, process_path)
    # init the tools module internal variables
    set_baseline_performance_report(get_resource_utilization_and_overall_statistics(baseline_performance))
    set_process_path(process_path)

    try:
        conversation = Conversation(
            model=Claude3.OPUS.value,
            tools=tools,
            system_instructions=compose_instructions(simulation_model_id),
        )
        conversation.run(
            """What if we increase the amount of resource named 'Carmen Finacse' to 3 and 'Esmeralda Clay' to 3?"""
        )
    except anthropic.BadRequestError as e:
        print(e)


if __name__ == "__main__":
    main()

# pylint: disable=fixme
# TODO: add another agent who runs the simulation and compares initial simulation model with the updated one
