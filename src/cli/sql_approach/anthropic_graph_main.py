"""
An approach to running agents using LangGraph for more explicit LLM steps and better control.
"""

import operator
from pathlib import Path
from typing import TypedDict, Union, Annotated, Sequence

from dotenv import load_dotenv
from langchain import hub
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, FunctionMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from anthropic_advanced_main import create_initial_simulation_model, tools
from llm_compiler_parser import LLMCompilerPlanParser
from simulation_copilot.anthropic import Claude3
from simulation_copilot.database import create_tables
from simulation_copilot.prompts import make_simulation_copilot_system_prompt
from simulation_copilot.prosimos_utils import (
    run_prosimos,
    get_resource_utilization_and_overall_statistics,
)
from simulation_copilot.tools.prosimos_relational_tools import (
    set_baseline_performance_report,
    set_process_path,
)

load_dotenv()
create_tables()
simulation_model_id = create_initial_simulation_model()
system_prompt = make_simulation_copilot_system_prompt(simulation_model_id)

# init the tools module internal variables
process_path = Path(__file__).parent.parent.parent.parent / "tests/test_data/PurchasingExample/process.bpmn"
baseline_performance = run_prosimos(simulation_model_id, process_path)
set_baseline_performance_report(get_resource_utilization_and_overall_statistics(baseline_performance))
set_process_path(process_path)

# creating an agent
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)
llm = ChatAnthropic(model=Claude3.OPUS.value, temperature=0, verbose=True)
agent_runnable = create_tool_calling_agent(llm, tools, prompt)

# planner


def create_planner(llm: BaseChatModel, tools: Sequence[BaseTool], base_prompt: ChatPromptTemplate):
    tool_descriptions = "\n".join(
        f"{i+1}. {tool.description}\n"
        for i, tool in enumerate(tools)  # +1 to offset the 0 starting index, we want it count normally from 1.
    )
    planner_prompt = base_prompt.partial(
        replan="",
        num_tools=len(tools) + 1,  # Add one because we're adding the join() tool at the end.
        tool_descriptions=tool_descriptions,
    )
    replanner_prompt = base_prompt.partial(
        replan=' - You are given "Previous Plan" which is the plan that the previous agent created along with the execution results '
        "(given as Observation) of each plan and a general thought (given as Thought) about the executed results."
        'You MUST use these information to create the next plan under "Current Plan".\n'
        ' - When starting the Current Plan, you should start with "Thought" that outlines the strategy for the next plan.\n'
        " - In the Current Plan, you should NEVER repeat the actions that are already executed in the Previous Plan.\n"
        " - You must continue the task index from the end of the previous one. Do not repeat task indices.",
        num_tools=len(tools) + 1,
        tool_descriptions=tool_descriptions,
    )

    def should_replan(state: list):
        # Context is passed as a system message
        return isinstance(state[-1], SystemMessage)

    def wrap_messages(state: list):
        return {"messages": state}

    def wrap_and_get_last_index(state: list):
        next_task = 0
        for message in state[::-1]:
            if isinstance(message, FunctionMessage):
                next_task = message.additional_kwargs["idx"] + 1
                break
        state[-1].content = state[-1].content + f" - Begin counting at : {next_task}"
        return {"messages": state}

    return (
        RunnableBranch(
            (should_replan, wrap_and_get_last_index | replanner_prompt),
            wrap_messages | planner_prompt,
        )
        | llm
        | LLMCompilerPlanParser(tools=tools)
    )


planner_prompt = hub.pull("wfh/llm-compiler")
planner = create_planner(llm, tools, planner_prompt)

# graph


class AgentState(TypedDict):
    """
    State of an agent that's getting passed between graph nodes.
    """

    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]


tool_executor = ToolExecutor(tools)


def run_planner(data):
    """Runs planner LLM on input."""
    agent_outcome = planner.invoke(data)
    return {"agent_outcome": agent_outcome}


def run_agent(data):
    """Runs LLM on input."""
    agent_outcome = agent_runnable.invoke(data)
    return {"agent_outcome": agent_outcome}


def execute_tools(data):
    """Executes tools on agent_outcome."""
    agent_action = data["agent_outcome"]
    if isinstance(agent_action, list):
        # https://github.com/langchain-ai/langgraph/blob/main/examples/agent_executor/base.ipynb?ref=blog.langchain.dev
        # the langgraph's example expects agent_action to be an object of type Union[AgentAction, AgentFinish], but
        # in our case it's a list of such objects; LLM can require multiple function calls, but we
        # don't want it for now to run anything in parallel, so we're expecting a list of one only
        if len(agent_action) > 1:
            print(f"[WARN] Unexpected behaviour: agent_action should be a list of one, got {agent_action}")
        agent_action = agent_action[0]
    result = tool_executor.invoke(agent_action)
    return {"intermediate_steps": [(agent_action, str(result))]}


def should_continue(data):
    """Conditional node to decide if to exit the pipeline or continue the execution."""
    if isinstance(data["agent_outcome"], AgentFinish):
        return "end"
    return "continue"


workflow = StateGraph(AgentState)
workflow.add_node("planner", run_planner)
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)
workflow.set_entry_point("planner")
workflow.add_conditional_edges("planner", should_continue, {"continue": "agent", "end": END})
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")

app = workflow.compile()

# output formatting


def print_output(out: dict[str, dict]):
    if "agent" in out:
        print(f"AGENT:\n")
        outcome = out["agent_outcome"]
        if isinstance(outcome, list) and isinstance(outcome[0], AgentAction):
            print(f"\t[")
        elif isinstance(outcome, AgentFinish):
            ...
        else:
            ...
        print(f"\t")


# pipeline run

inputs = {
    # "input": "What if we increase the amount of resource named 'Carmen Finacse' to 3 and 'Esmeralda Clay' to 3?",
    "input": "What would happen if we get 20% more cases next week?",
    "chat_history": [],
}
for output in app.stream(inputs):
    print(output)
