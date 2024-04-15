# This is the second approach to generate simulation scenarios using LLM.
#
# The idea is to convert all the necessary data (e.g., a simulation model) into
# SQL databases and operate it through SQL queries.
from typing import Union, Sequence

from dotenv import load_dotenv
from langchain import hub
from langchain.agents import (
    AgentExecutor,
    BaseMultiActionAgent,
    BaseSingleActionAgent,
    create_openai_functions_agent,
    create_xml_agent,
)
from langchain.agents.output_parsers import XMLAgentOutputParser
from langchain_anthropic import ChatAnthropic
from langchain_core.language_models import BaseLanguageModel
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnablePassthrough
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI

from cli.sql_approach.init_db import (
    SQL_SCHEMA_PATH,
    tables_schema,
)
from simulation_copilot.database import create_tables
from simulation_copilot.database import engine
from simulation_copilot.tools.sql import run_sqlite3_query

tools = [
    run_sqlite3_query,
]


def make_openai_instructions():
    instructions = """You are an assistant who helps with preparing of a business process simulation model.
    The model is represented by a set of tables in a SQL database.
    Reuse calendars for resources if possible.

    Below are the SQL schemas for available models.

    Note: In activity distributions, the distribution name is the name of the distribution
    and the parameters is a list of parameters for this specific distribution.
    The name and number of distribution parameters depend on the distribution.

    Note: Always use full column qualifiers in the SQL statement.

    Note: If you are lacking some information, you can query the database given the table schemas below.
    Always try to figure out the information from the database first before asking the user.
    """
    with open(SQL_SCHEMA_PATH) as f:
        instructions += f.read()
    return instructions


def make_anthropic_prompt():
    context = instructions()
    context += """You have access to the following tools:

{tools}

In order to use a tool, you can use <tool></tool> and <tool_input></tool_input> tags. You will then get back a response in the form <observation></observation>
For example, if you have a tool called 'search' that could run a google search, in order to search for the weather in SF you would respond:

<tool>search</tool><tool_input>weather in SF</tool_input>
<observation>64 degrees</observation>

When you are done, respond with a final answer between <final_answer></final_answer>. For example:

<final_answer>The weather in SF is 64 degrees</final_answer>

Think step-by-step.

Begin!

Previous Conversation:
{chat_history}

Question: {input}
{agent_scratchpad}"""
    return context


def instructions():
    context = f"""You are an assistant who helps with preparing of a business process simulation model. The model is represented by a set of tables in a SQL database. Reuse calendars for resources if possible.

Note: In activity distributions, the distribution name is the name of the distribution and the parameters is a list of parameters for this specific distribution. The name and number of distribution parameters depend on the distribution.
Note: Always use full column qualifiers in the SQL statement.
Note: If you are lacking some information, you can query the database given the table schemas below. Always try to figure out the information from the database first before asking the user.

Below are the SQL schemas for available models:

{tables_schema()}
"""
    return context


def make_openai_gpt4_agent(instructions: str, tools: list):
    llm = ChatOpenAI(model="gpt-4-0125-preview", temperature=0)
    base_prompt = hub.pull("langchain-ai/openai-functions-template")
    prompt = base_prompt.partial(instructions=instructions)
    return create_openai_functions_agent(llm, tools, prompt)


def make_anthropic_claude3_agent(prompt: str, tools: list):
    # Models names ranked by "intelligence" and cost (most expensive and intelligent first):
    # - claude-3-opus-20240229
    # - claude-3-sonnet-20240229
    # - claude-3-haiku-20240307 (returns XML parser error)
    llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0, streaming=False).bind_tools(tools)
    # prompt = ChatPromptTemplate.from_messages([("human", prompt)])
    prompt = hub.pull("hwchase17/xml-agent-convo")
    prompt = prompt.partial(instructions=prompt)
    # return create_anthropic_functions_agent(llm, tools, prompt)
    return create_xml_agent(llm, tools, prompt)


def create_anthropic_functions_agent(
    llm: Union[BaseLanguageModel, Runnable],
    tools: Sequence[BaseTool],
    prompt: ChatPromptTemplate,
):
    if "agent_scratchpad" not in prompt.input_variables:
        raise ValueError(
            "Prompt must have input variable `agent_scratchpad`, but wasn't found. "
            f"Found {prompt.input_variables} instead."
        )
    agent = (
        RunnablePassthrough.assign(agent_scratchpad=lambda x: convert_intermediate_steps(x["intermediate_steps"]))
        | prompt.partial(tools=convert_tools(tools), chat_history="")
        | llm.bind(stop=["</tool_input>", "</final_answer>"])
        | XMLAgentOutputParser()
    )
    return agent


def convert_intermediate_steps(intermediate_steps):
    log = ""
    for action, observation in intermediate_steps:
        log += (
            f"<tool>{action.tool}</tool><tool_input>{action.tool_input}"
            f"</tool_input><observation>{observation}</observation>"
        )
    return log


def convert_tools(tools: Sequence[BaseTool]):
    return "\n".join([f"{tool.name}: {tool.description}" for tool in tools])


def make_agent_executor(
    agent: Union[BaseSingleActionAgent, BaseMultiActionAgent, Runnable],
    tools: Sequence[BaseTool],
):
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        handle_parsing_errors=True,
    )


def test_zero(agent_executor: AgentExecutor):
    print(agent_executor.invoke({"input": "What data models do you have access to?"}))


def test_one(agent_executor: AgentExecutor):
    print(
        agent_executor.invoke(
            {
                "input": "Using the SQL tool, create a calendar with the following intervals and give me back the ID of the calendar: 8.30am to 7.30pm Monday to Wednesday, 11am to 9pm Thursday and Friday, and 9am to 5pm Saturday and Sunday."
            }
        )
    )


def test_two(agent_executor: AgentExecutor):
    print(
        agent_executor.invoke(
            {"input": "Modify calendar with ID = 1 the week-end working hours, make it from 2pm to 9pm."}
        )
    )


def test_three(agent_executor: AgentExecutor):
    print(
        agent_executor.invoke(
            {
                "input": """
    Create a basic resource profile with two resources with names 'Junior' and 'Senior'
    who work from 9am to 5pm Monday to Friday with a 1-hour lunch break.
    There're 3 Juniors and 2 Seniors.
    The Juniors cost $20/hour and the Seniors cost $30/hour.
    The Junior is assigned to activity 'A' with a normal distribution with mean 60 and standard deviation 2.
    The Senior is assigned to activity 'B' with a normal distribution with mean 15 and standard deviation 3.
    """
            }
        )
    )


def test_four(agent_executor: AgentExecutor):
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


def test_five(agent_executor: AgentExecutor):
    print(
        agent_executor.invoke(
            {
                "input": """
    Generate a simulation model with 2 resource profiles, which has 2 calendars, and gateway probabilties.
    Calendar 'BusyHours' specifies working hours from 8am to 9pm Monday to Friday, from 9am to 5pm on Saturday, and from 10am to 4pm on Sunday.
    Calendar 'NormalHours' specifies working hours from 9am to 5pm Monday to Friday, and from 10am to 4pm on Saturday and Sunday.
    There are 2 resource profiles, 'Busy' and 'Normal'.
    Profile 'Busy' has 2 resources, 'Junior' and 'Senior', with the quantity of 5 and 3, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'BusyHours'.
    Profile 'Normal' has 2 resources, 'Junior' and 'Senior', with the quantity of 1 and 1, 10 and 20 EUR per hour, and assigned activities A, B, and C with the calendar 'NormalHours'.
    Also, add gateway probabilities for the gateways 'Gateway1' and 'Gateway2' with the outgoing sequence flows 'SequenceFlow1' and 'SequenceFlow2' with the probabilities 0.3 and 0.7 for 'Gateway1' and 0.6 and 0.4 for 'Gateway2'.
    """
            }
        )
    )


def main():
    global tools

    # OPENAI_ORGANIZATION_ID, OPENAI_API_KEY are required to be set in the .env file or as environment variables.
    load_dotenv()

    create_tables(engine)

    agent = make_anthropic_claude3_agent(make_anthropic_prompt(), tools)
    executor = make_agent_executor(agent, tools)
    test_one(executor)


if __name__ == "__main__":
    main()
