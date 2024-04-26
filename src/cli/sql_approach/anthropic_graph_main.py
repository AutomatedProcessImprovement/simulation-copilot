"""
An approach to running agents using LangGraph for more explicit LLM steps and better control.
"""
import operator
from pathlib import Path
from typing import TypedDict, Union, Annotated

from dotenv import load_dotenv
from langchain.agents.tool_calling_agent.base import create_tool_calling_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor

from anthropic_advanced_main import create_initial_simulation_model, tools
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


def run_agent(data):
    """Runs LLM on input."""
    agent_outcome = agent_runnable.invoke(data)
    return {"agent_outcome": agent_outcome}


def execute_tools(data):
    """Executes tools on agent_outcome."""
    agent_action = data["agent_outcome"]
    if isinstance(agent_action, list):
        if len(agent_action) > 1:
            print(f"[WARN] Unexpected behaviour: agent_action should be a list of one, got {agent_action}")
        agent_action = agent_action[0]
    result = tool_executor.invoke(agent_action)
    return {"intermediate_steps": [(agent_action, str(result))]}


def should_continue(data):
    """Conditional node to decide if exit the pipeline or continue the execution."""
    if isinstance(data["agent_outcome"], AgentFinish):
        return "end"
    return "continue"


workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {"continue": "action", "end": END})
workflow.add_edge("action", "agent")

app = workflow.compile()

inputs = {
    "input": "What if we increase the amount of resource named 'Carmen Finacse' to 3 and 'Esmeralda Clay' to 3?",
    "chat_history": [],
}
for output in app.stream(inputs):
    print(output)
