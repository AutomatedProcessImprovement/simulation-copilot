# This was the initial approach to generating simulation scenarios--by using
# Python function as LLM tools directly.
#
# The problem was that LLM needed to handle input and output variables of a big size
# (e.g., a calendar has many intervals, resource profile has multiple calendars, etc.)
# which makes it fail more often. Also, it consumes a lot of tokens just for passing
# variables from one tool to another.
#
# Ths solution was to convert the simulation model to a SQL database and run 
# SQL queries instead of calling Python functions.

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


# print(
#     agent_executor.invoke(
#         {
#             "input": """
# Generate a simulation model with a resource model with 2 resource profiles, which has 2 calendars, and gateway probabilties.
# Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
# Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
# Resource model has 2 resource profiles, 'Busy' and 'Normal'.
# Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
# Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
# Also, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.
# """
#         }
#     )
# )


print(
    agent_executor.invoke(
        {
            "input": """
Given the following simulation model set the number of 'Junior' resources in the 'Busy' profile to 10: 

SimulationModel(resource_model=ResourceModel(profiles=[ResourceProfile(id='5bb14ad39ac44a42b95e7e97c40cba75', name='Busy', resources=[Resource(id='79e2bfd841a841e6a9122f01c2f1192e', name='Junior', amount=5, cost_per_hour=10.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='5f2bb5de72cb42d5ad06e188f0f8a9df', name='Senior', amount=3, cost_per_hour=20.0, calendar_id='c81ead98cd894ae39b90efe129d496c9', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])]), ResourceProfile(id='d8ac0d1650d54dc4aaedd4cfa3172190', name='Normal', resources=[Resource(id='da6f7a698f4943348a6eb998a98854a6', name='Junior', amount=1, cost_per_hour=10.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))]), Resource(id='6cc6686fdc4546e48ca41f0cec183d6f', name='Senior', amount=1, cost_per_hour=20.0, calendar_id='3b474c4e76184526b3b91f67540045d4', assigned_activities=[ActivityDistribution(activity_id='A', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='B', distribution=Distribution(name='uniform', parameters=[1.0, 2.0])), ActivityDistribution(activity_id='C', distribution=Distribution(name='uniform', parameters=[1.0, 2.0]))])])], calendars=[Calendar(id='c81ead98cd894ae39b90efe129d496c9', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=8, minute=0), end_time=Time(hour=21, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SATURDAY: 'Saturday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SUNDAY: 'Sunday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))]), Calendar(id='3b474c4e76184526b3b91f67540045d4', intervals=[CalendarInterval(start_day=<Day.MONDAY: 'Monday'>, end_day=<Day.FRIDAY: 'Friday'>, start_time=Time(hour=9, minute=0), end_time=Time(hour=17, minute=0)), CalendarInterval(start_day=<Day.SATURDAY: 'Saturday'>, end_day=<Day.SUNDAY: 'Sunday'>, start_time=Time(hour=10, minute=0), end_time=Time(hour=16, minute=0))])]), gateway_probabilities=[GatewayProbabilities(gateway_id='Gateway1', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.3), PathProbability(path_id='SequenceFlow2', probability=0.7)]), GatewayProbabilities(gateway_id='Gateway2', outgoing_paths=[PathProbability(path_id='SequenceFlow1', probability=0.6), PathProbability(path_id='SequenceFlow2', probability=0.4)])])
"""
        }
    )
)
