"""In this script, we use the Anthropic SDK instead of LangChain.
"""
import anthropic
from dotenv import load_dotenv

from simulation_copilot.anthropic import Conversation
from simulation_copilot.anthropic.conversation import Claude3
from simulation_copilot.database import create_tables, tables_schema
from simulation_copilot.tools.prosimos_relational_tools import (
    create_simulation_model,
    get_simulation_model,
    change_resource_amount,
    add_resource_to_profile,
    remove_resource_from_profile_by_id,
    create_calendar_with_intervals,
    create_distribution,
    add_case_arrival,
)
from utils import print_all_simulation_models  # pylint: disable=wrong-import-order

# pylint: disable=duplicate-code
tools = [
    create_simulation_model,
    get_simulation_model,
    change_resource_amount,
    add_resource_to_profile,
    remove_resource_from_profile_by_id,
    create_calendar_with_intervals,
    create_distribution,
    add_case_arrival,
]


def instructions():
    """
    System instructions for the assistant.
    """
    # pylint: disable=line-too-long
    context = f"""You are an assistant who helps with preparing of a business process simulation model. The model is represented by a set of tables in a SQL database. Reuse calendars whenever possible.

Note: In activity distributions, the distribution name is the name of the distribution and the parameters is a list of parameters for this specific distribution. The name and number of distribution parameters depend on the distribution.
Note: If you are lacking some information, query the database using the provided tools. Always try to query the lacking information from the database first before asking the user.

Below is the SQL schema for simulation model tables;

{tables_schema()}

You don't need to query the database directly, but you can use the provided tools to interact with the database.
Note: Use one tool at a time, then, wait for a new request to adjust input parameters for the next tool call if needed.
"""
    return context


def main():
    # pylint: disable=missing-function-docstring,line-too-long

    load_dotenv()
    create_tables()

    try:
        conversation = Conversation(model=Claude3.OPUS.value, tools=tools, system_instructions=instructions())
        conversation.run(
            "Create a simulation model with case arrival calendar of 9am to 5pm on weekdays with a mean inter-arrival time of 30 minutes and exponential distribution."
        )
    except anthropic.BadRequestError as e:
        print(e)
    finally:
        print_all_simulation_models()


if __name__ == "__main__":
    load_dotenv()
    main()

# pylint: disable=fixme
# TODO: handle error in tools
# TODO: add another agent who runs the simulation and compares initial simulation model with the updated one
