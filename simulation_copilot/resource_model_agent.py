from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

from simulation_copilot.tools.bps_model import generate_bps_model
from simulation_copilot.tools.calendar import generate_calendar
from simulation_copilot.tools.gateway_probabilities import (
    generate_gateway_probabilities,
)
from simulation_copilot.tools.resource_model import generate_resource_model
from simulation_copilot.tools.resource_profile import generate_resource_profile

# NOTE: TAVILY_API_KEY, OPENAI_ORGANIZATION_ID, OPENAI_API_KEY are required
#   to be set in the .env file or as environment variables
load_dotenv()


tavily_tool = TavilySearchResults()

tools = [
    tavily_tool,
    generate_calendar,
    generate_resource_profile,
    generate_resource_model,
    generate_gateway_probabilities,
    generate_bps_model,
]

instructions = """You are an assistant who helps with business process simulation. 
You can help with generating a calendar for a resource.
Use the SimulationModel class as output for the generate_bps_model tool whenever possible.
"""
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
#             "input": "generate a calendar for a resource that works 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
#         }
#     )
# )

# print(
#     agent_executor.invoke(
#         {
#             "input": "generate a resource profile for the resource Operator with a quantity of 4, cost 20 EUR per hour who works on activities A, B, and C."
#         }
#     )
# )

# print(
#     agent_executor.invoke(
#         {
#             "input": """
# Generate a resource model with 2 resource profiles and 2 calendars.
# Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
# Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
# Resource model has 2 resource profiles, 'Busy' and 'Normal'.
# Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
# Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
# """
#         }
#     )
# )


print(
    agent_executor.invoke(
        {
            "input": """
Generate a simulation model with a resource model with 2 resource profiles, which has 2 calendars, and gateway probabilties.
Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
Resource model has 2 resource profiles, 'Busy' and 'Normal'.
Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
Also, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.
"""
        }
    )
)
