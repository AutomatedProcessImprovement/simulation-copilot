from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

from simulation_copilot.tools.calendar import generate_calendar
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
]

instructions = """You are an assistant who helps with business process simulation. 
You can help with generating a calendar for a resource."""
base_prompt = hub.pull("langchain-ai/openai-functions-template")
prompt = base_prompt.partial(instructions=instructions)

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
agent = create_openai_functions_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
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

print(
    agent_executor.invoke(
        {
            "input": """
Generate a resource model with 2 resource profiles and 2 calendars. 
Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
Resource model has 2 resource profiles, 'Busy' and 'Normal'.
Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
"""
        }
    )
)
