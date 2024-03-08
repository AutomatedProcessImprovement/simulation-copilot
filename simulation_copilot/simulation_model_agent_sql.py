from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI

from simulation_copilot.tools.sql import run_sql

# NOTE: OPENAI_ORGANIZATION_ID, OPENAI_API_KEY are required to be set in the .env file or as environment variables.
load_dotenv()


tools = [
    run_sql,
]

instructions = """You are an assistant who helps with preparing of a business process simulation model.
The model is represented by a set of tables in a SQL database.
Reuse calendars for resources if possible.

Below are the SQL schemas for available models.

Note: In activity distributions, the distribution name is the name of the distribution
and the parameters is a list of parameters for this specific distribution serialized as a string joined with a comma.

Note: Always use full column qualifiers in the SQL statement.

Note: If you you are lacking some information, you can query the database given the table schemas below.
Always try to figure out the information from the database first before asking the user.
"""
with open("simulation_copilot/schemas.sql") as f:
    instructions += f.read()
print(f"Instructions: {instructions}")

base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)

llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True,
)


# print(
#     agent_executor.invoke(
#         {
#             "input": "Using the SQL tool, create a calendar with the following intervals and give me back the ID of the calendar: 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
#         }
#     )
# )

# print(
#     agent_executor.invoke(
#         {
#             "input": "Modify calendar with ID = 1 the week-end working hours, make it from 2pm to 9pm."
#         }
#     )
# )

# print(
#     agent_executor.invoke(
#         {
#             "input": """
# Create a basic resource profile with two resources with names 'Junior' and 'Senior'
# who work from 9am to 5pm Monday to Friday with a 1-hour lunch break.
# There're 3 Juniors and 2 Seniors.
# The Juniors cost $20/hour and the Seniors cost $30/hour.
# The Junior is assigned to activity 'A' with a normal distribution with mean 60 and standard deviation 2.
# The Senior is assigned to activity 'B' with a normal distribution with mean 15 and standard deviation 3.
# """
#         }
#     )
# )


print(
    agent_executor.invoke(
        {
            "input": """
The mean time for activity 'A' has increased to 90 minutes.
Update the distribution for the Junior resource.
"""
        }
    )
)
