"""Conversation API for running conversations with Anthropic LLMs and using function tools.

Typical usage example:

TODO: ...
"""

import logging
from enum import Enum
from functools import partial
from typing import List, Optional, Dict, Union, Literal

from anthropic import Anthropic
from anthropic.types import TextBlock
from anthropic.types.beta.tools import ToolsBetaMessage, ToolUseBlock
from langchain_core.tools import StructuredTool
from pydantic import BaseModel
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
    def print_text(text: str, role: str):
        for line in text.splitlines():
            _print_role(f"  {line}", role)

    for block in blocks:
        text = ""
        if isinstance(block, ToolUseBlock):
            role = "tool_use"  # role might be adjusted depending on the block type
            text = f"[wants to run '{block.name}' with input {block.input}]"
        elif isinstance(block, TextBlock):
            text = block.text
        elif "type" in block and block["type"] == "tool_result":
            role = "tool_result"
            text = block["content"]  # List[TextBlock]
        else:
            logging.warning(f"Unknown text block: {block}")

        if not text:  # content may be missing, e.g., tools output is empty
            if role == "tool_result":
                _print_role(f"  [no output from function]", role)
            else:
                _print_role(f"  [no content]", role)
        else:
            if isinstance(text, str):
                print_text(text, role)
            elif isinstance(text, list):  # tool_result, List[TextBlock] as dict
                for text_block in text:
                    print_text(text_block["text"], role)


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


class _ToolResult(BaseModel):
    tool_block: ToolUseBlock
    output: object


def _run_tool_block(block: ToolUseBlock, tools: List[StructuredTool]) -> Optional[_ToolResult]:
    if block is None:
        print("Calling run_tool_block with empty block: %s" % block)
        return None
    tool = find_tool(block.name, tools)
    print(f"* [running {tool} on {block}]")
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


class ContentBlock(BaseModel):  # ToolResultBlockParam from Anthropic
    type: Literal["tool_result"] = "tool_result"
    content: List[TextBlock] = []
    tool_use_id: Optional[str] = None
    is_error: Optional[bool] = None

    @staticmethod
    def from_str(message: str, tool_use_id: str) -> "ContentBlock":
        return ContentBlock(tool_use_id=tool_use_id, content=[TextBlock(type="text", text=message)])


class RequestMessage(BaseModel):
    role: Literal["user", "assistant"] = "user"
    content: List[ContentBlock] = []

    def to_json_dict(self) -> dict:
        return self.model_dump(mode="json", exclude_none=True)


def _compose_message_from_tools_output(
    tools_output: List[_ToolResult],
) -> RequestMessage:
    return RequestMessage(
        content=[
            ContentBlock.from_str(message=str(result.output), tool_use_id=result.tool_block.id)
            for result in tools_output
        ]
    )


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
            temperature=0.1,
        )  # partial function with most of the parameters pre-filled
        self._max_tools_invocations = max_tools_invocations

    def run(self, user_prompt: str):
        # first request
        message = {"role": Role.USER.value, "content": user_prompt}
        response = self._request_and_append_messages(message=message)

        # subsequent requests
        while not (
            response.stop_reason == "end_turn"
            or response.stop_reason == "stop_sequence"
            or self._max_tools_invocations == 0
        ):
            self._max_tools_invocations -= 1

            tool_blocks = _tool_blocks_from_response(response)
            if len(tool_blocks) == 0:
                print("No tools blocks found")
                return

            # Avoid running many tools:
            # often, Claude3 OPUS wants to execute several tools at once instead of running them sequentially,
            # we pick only the first tool call here and execute it instead of all tool blocks,
            # so that LLM can adjust input parameters for the next tools
            if len(tool_blocks) > 1:
                tool_blocks = tool_blocks[:1]

            tools_output = [_run_tool_block(block, self.tools) for block in tool_blocks]
            if len(tools_output) == 0:  # no tools output, nothing to send to LLM, exit
                print("No tools results produced")
                return

            tools_message = _compose_message_from_tools_output(tools_output)
            response = self._request_and_append_messages(tools_message.to_json_dict())

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
