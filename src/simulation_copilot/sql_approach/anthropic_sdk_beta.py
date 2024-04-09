# In this script, we use the Anthropic SDK instead of LangChain.
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import List, Optional

from anthropic import Anthropic
from anthropic.types import TextBlock
from anthropic.types.beta.tools import ToolsBetaMessage, ToolUseBlock
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool

from simulation_copilot.lib.tools.sql import run_sqlite3_query
from simulation_copilot.sql_approach.db import engine
from simulation_copilot.sql_approach.init_db import tables_schema, create_tables

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


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Claude3(str, Enum):
    OPUS = "claude-3-opus-20240229"
    SONNET = "claude-3-sonnet-20240229"
    HAIKU = "claude-3-haiku-20240307"


def find_tool(name: str, tools: List[StructuredTool]):
    for t in tools:
        if t.name == name:
            return t
    return None


@dataclass
class ToolResult:
    tool_block: ToolUseBlock
    output: object


def run_tool_block(block: ToolUseBlock, tools: List[StructuredTool]) -> Optional[ToolResult]:
    if block is None:
        print("Calling run_tool_block with empty block: %s" % block)
        return None
    tool = find_tool(block.name, tools)
    output = tool.func(**block.input)
    return ToolResult(tool_block=block, output=output)


def tool_blocks_from_response(response: ToolsBetaMessage) -> List[ToolUseBlock]:
    if response.stop_reason != "tool_use":
        return []
    blocks: List[ToolUseBlock] = []
    for msg in response.content:
        if msg.type != "tool_use":
            continue
        blocks.append(msg)
    return blocks


def pretty_print(msg: ToolsBetaMessage):
    try:
        role = getattr(msg, "role", "unknown").upper()
        reason = getattr(msg, "stop_reason", "unknown")
        content = getattr(msg, "content", [])
        print(f"\n{role} [stop_reason={reason}]:")
        for m in content:
            if isinstance(m, TextBlock):
                for line in m.text.splitlines():
                    print(f"\t{line}")
            else:
                print(f"\t{m}")
    except Exception:
        print(msg)


def simplify_tool_beta_message(msg: ToolsBetaMessage) -> dict:
    # Anthropic complains about extra inputs when sending back ToolsBetaMessage in messages:
    #   `messages.1.id: Extra inputs are not permitted`.
    # To fix it, we simplify the response be removing unnecessary fields.
    return {"role": msg.role, "content": msg.content}


def format_tool(tool: StructuredTool):
    return {"name": tool.name, "description": tool.description.strip(), "input_schema": tool.args_schema.schema()}


def format_tools(tools: list[StructuredTool]):
    return [format_tool(tool) for tool in tools]


def main():
    load_dotenv()
    create_tables(engine)

    client = Anthropic()
    call = partial(
        client.beta.tools.messages.create,
        model=Claude3.OPUS.value,
        max_tokens=4096,  # max output for all Anthropic models
        tools=format_tools(tools),
        system=instructions(),
    )  # partial function with most of the parameters pre-filled

    messages = [{"role": Role.USER.value, "content": "Create a calendar 9-5 pm."}]  # accumulates message history
    response = None  # the most recent response
    end_condition_met = False  # flag for stopping tool execution loop

    # initial request
    response = call(messages=messages)
    messages.append(simplify_tool_beta_message(response))
    pretty_print(response)

    while not end_condition_met:  # tool execution loop
        # tool calling
        results = []
        for block in tool_blocks_from_response(response):
            results.append(run_tool_block(block, tools))

        if len(results) == 0:
            print("Done")
            return

        # sending tool results
        result_message = {"role": Role.USER.value, "content": []}
        for result in results:
            result_message["content"].append(
                {
                    "type": "tool_result",
                    "tool_use_id": result.tool_block.id,
                    "content": result.output,
                }
            )
        messages.append(result_message)

        print("Sending back to Claude:")
        pretty_print(result_message)
        response = call(messages=messages)
        pretty_print(response)
        if response.stop_reason == "end_turn" or response.stop_reason == "stop_sequence":
            end_condition_met = True


if __name__ == "__main__":
    load_dotenv()
    main()


# TODO: add a function to dump database to a simulation model format
# TODO: execute database dump at the end of the message exchange
