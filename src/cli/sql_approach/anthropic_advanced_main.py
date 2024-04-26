"""In this script, we use the Anthropic SDK instead of LangChain.
"""

import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

from simulation_copilot.anthropic import Conversation
from simulation_copilot.anthropic.conversation import Claude3
from simulation_copilot.database import create_tables, get_session
from simulation_copilot.prompts import make_simulation_copilot_system_prompt
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


def create_initial_simulation_model() -> int:
    """
    Loads the initial simulation model from a JSON file and creates necessary records in the database.
    Returns the ID of the relational model.
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
    simulation_model_id = create_initial_simulation_model()
    baseline_performance = run_prosimos(simulation_model_id, process_path)
    # init the tools module internal variables
    set_baseline_performance_report(get_resource_utilization_and_overall_statistics(baseline_performance))
    set_process_path(process_path)

    try:
        conversation = Conversation(
            model=Claude3.OPUS.value,
            tools=tools,
            system_instructions=make_simulation_copilot_system_prompt(simulation_model_id),
        )
        conversation.run(
            """What if we increase the amount of resource named 'Carmen Finacse' to 3 and 'Esmeralda Clay' to 3?"""
        )
    except anthropic.BadRequestError as e:
        print(e)


if __name__ == "__main__":
    main()
