# In this script, we use the Anthropic SDK instead of LangChain.

from dotenv import load_dotenv

from cli.sql_approach.init_db import tables_schema
from simulation_copilot.anthropic import Claude3
from simulation_copilot.anthropic import Conversation
from simulation_copilot.database import create_tables
from simulation_copilot.database import engine
from simulation_copilot.tools.sql import run_sqlite3_query

tools = [run_sqlite3_query]


def instructions():
    context = f"""You are an assistant who helps with preparing of a business process simulation model. The model is represented by a set of tables in a SQL database. Reuse calendars for resources if possible.

Note: In activity distributions, the distribution name is the name of the distribution and the parameters is a list of parameters for this specific distribution. The name and number of distribution parameters depend on the distribution.
Note: Always use full column qualifiers in the SQL statement.
Note: If you are lacking some information, you can query the database given the table schemas below. Always try to figure out the information from the database first before asking the user.

Below are the SQL schemas for available models:

{tables_schema()}
"""
    return context


def main():
    load_dotenv()
    create_tables(engine)

    conversation = Conversation(model=Claude3.OPUS.value, tools=tools, system_instructions=instructions())
    conversation.run("Create a calendar 9-5 pm.")


if __name__ == "__main__":
    load_dotenv()
    main()


# TODO: ensure Prosimos compatibility
# TODO: execute database dump at the end of the message exchange

# TODO: handle error in tools
# TODO: instead of the generic SQL tool, use predefined SQL functions, so LLM needs to provide only params
