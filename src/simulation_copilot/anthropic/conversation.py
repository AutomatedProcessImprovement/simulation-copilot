"""Conversation API for running conversations with Anthropic LLMs and using function tools.

Typical usage example:

TODO: ...
"""

import logging
from dataclasses import dataclass
from enum import Enum
from functools import partial
from typing import List, Optional, Dict, Union

from anthropic import Anthropic
from anthropic.types import TextBlock
from anthropic.types.beta.tools import ToolsBetaMessage, ToolUseBlock
from langchain_core.tools import StructuredTool
from tenacity import retry, stop_after_attempt
from termcolor import colored


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Claude3(str, Enum):
    OPUS = "claude-3-opus-20240229"
    SONNET = "claude-3-sonnet-20240229"
    HAIKU = "claude-3-haiku-20240307"


def pretty_print(msg: Union[ToolsBetaMessage, Dict]):
    try:
        role: str = ""
        reason: Optional[str] = None
        content: Union[List, str] = []

        if isinstance(msg, Dict):
            role = msg.get("role")
            if not role:
                role = msg.get("type")
            reason = msg.get("stop_reason")
            content = msg.get("content")
        elif isinstance(msg, ToolsBetaMessage):
            role = getattr(msg, "role", None)
            if not role:
                getattr(msg, "type")
            reason = getattr(msg, "stop_reason", None)
            content = getattr(msg, "content", [])
        role = role.lower()

        # header
        if reason:
            _print_role(f"\n{role.upper()} [stop_reason={reason}]:", role)
        else:
            _print_role(f"\n{role.upper()}:", role)

        # body
        if isinstance(content, str):
            _print_role(f"  {content}", role)
        else:
            _print_blocks(content, role)

    except Exception as e:
        logging.exception(e)
        print(msg)


def _print_blocks(blocks: List, role: str):
    for block in blocks:
        text = ""
        if isinstance(block, ToolUseBlock):
            role = "tool_use"  # role might be adjusted depending on the block type
            text = f"[running tool '{block.name}' with input {block.input}]"
        elif isinstance(block, TextBlock):
            text = block.text
        elif "type" in block and block["type"] == "tool_result":
            role = "tool_result"
            text = block["content"]
        else:
            logging.warning(f"Unknown text block: {block}")

        if not text:  # content may be missing, e.g., tools output is empty
            if role == "tool_result":
                _print_role(f"  [no output from function]", role)
            else:
                _print_role(f"  [no content]", role)
        else:
            for line in text.splitlines():
                _print_role(f"  {line}", role)


def _print_role(s: str, role: str):
    role_to_color = {
        "user": "green",
        "assistant": "blue",
        "tool_use": "magenta",
        "tool_result": "magenta",
        "unknown": "red",
    }
    print(colored(s, role_to_color[role]))


def find_tool(name: str, tools: List[StructuredTool]):
    for t in tools:
        if t.name == name:
            return t
    return None


def format_tool(tool: StructuredTool):
    return {
        "name": tool.name,
        "description": tool.description.strip(),
        "input_schema": tool.args_schema.schema(),
    }


def format_tools(tools: list[StructuredTool]):
    return [format_tool(tool) for tool in tools]


@dataclass
class _ToolResult:
    tool_block: ToolUseBlock
    output: object


def _run_tool_block(block: ToolUseBlock, tools: List[StructuredTool]) -> Optional[_ToolResult]:
    if block is None:
        print("Calling run_tool_block with empty block: %s" % block)
        return None
    tool = find_tool(block.name, tools)
    output = str(tool.func(**block.input))  # only str or a list of content blocks are allowed
    return _ToolResult(tool_block=block, output=output)


def _tool_blocks_from_response(response: ToolsBetaMessage) -> List[ToolUseBlock]:
    if response.stop_reason != "tool_use":
        return []
    blocks: List[ToolUseBlock] = []
    for msg in response.content:
        if msg.type != "tool_use":
            continue
        blocks.append(msg)
    return blocks


def _simplify_tool_beta_message(msg: ToolsBetaMessage) -> dict:
    # Anthropic complains about extra inputs when sending back ToolsBetaMessage in messages:
    #   `messages.1.id: Extra inputs are not permitted`.
    # To fix it, we simplify the response be removing unnecessary fields.
    return {"role": msg.role, "content": msg.content}


def _compose_message_from_tools_output(tools_output: List[_ToolResult]):
    msg = {"role": Role.USER.value, "content": []}
    for result in tools_output:
        msg["content"].append(
            {
                "type": "tool_result",
                "tool_use_id": result.tool_block.id,
                "content": result.output,
            }
        )
    return msg


class Conversation:
    def __init__(
        self,
        model: str,
        tools: List[StructuredTool],
        max_tokens: int = 4096,
        max_tools_invocations: int = 10,
        system_instructions: str = "",
    ):
        assert max_tokens <= 4096, "Maximum output is 4096 tokens"
        self.tools = tools
        self.messages = []
        self._client = Anthropic()
        self._call = partial(
            self._client.beta.tools.messages.create,
            model=model,
            tools=format_tools(tools),
            max_tokens=max_tokens,
            system=system_instructions,
        )  # partial function with most of the parameters pre-filled
        self._max_tools_invocations = max_tools_invocations

    def run(self, user_prompt: str):
        # first request
        message = {"role": Role.USER.value, "content": user_prompt}
        response = self._request_and_append_messages(message=message)

        # subsequent requests
        tool_blocks = _tool_blocks_from_response(response)
        if len(tool_blocks) == 0:
            return
        while not (
            response.stop_reason == "end_turn"
            or response.stop_reason == "stop_sequence"
            or self._max_tools_invocations == 0
        ):
            self._max_tools_invocations -= 1

            tools_output = [_run_tool_block(block, self.tools) for block in tool_blocks]
            if len(tools_output) == 0:  # no tools output, nothing to send to LLM, exit
                return

            tools_message = _compose_message_from_tools_output(tools_output)
            response = self._request_and_append_messages(tools_message)

    @retry(stop=stop_after_attempt(3))
    def _request_and_append_messages(self, message: Dict) -> ToolsBetaMessage:
        assert (
            message["role"] == Role.USER.value
        ), f"The last message before sending a request must be from user, got {message}"
        self.messages.append(message)
        pretty_print(message)
        response = self._call(messages=self.messages)
        self.messages.append(_simplify_tool_beta_message(response))
        pretty_print(response)
        return response
