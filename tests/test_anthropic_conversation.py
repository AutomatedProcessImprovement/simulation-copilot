# pylint: disable=missing-module-docstring,missing-class-docstring,missing-function-docstring
import unittest

from anthropic.types import TextBlock
from anthropic.types.beta.tools import ToolUseBlock

from simulation_copilot.anthropic.conversation import (
    _ToolResult,
    _compose_message_from_tools_output,
    RequestMessage,
    ContentBlock,
)


class TestAnthropicConversation(unittest.TestCase):
    def test_tool_result_composed_ok(self):
        results = [
            _ToolResult(tool_block=ToolUseBlock(id="1", input=None, name="tool1", type="tool_use"), output="output1"),
            _ToolResult(tool_block=ToolUseBlock(id="2", input=None, name="tool2", type="tool_use"), output="output2"),
            _ToolResult(tool_block=ToolUseBlock(id="3", input=None, name="tool3", type="tool_use"), output=1),
        ]

        message = _compose_message_from_tools_output(results)

        self.assertTrue(isinstance(message, RequestMessage))
        self.assertTrue(message.role == "user")
        self.assertTrue(len(message.content) == len(results))
        self.assertTrue(isinstance(message.content[0], ContentBlock))
        self.assertEqual(message.content[0].type, "tool_result")
        self.assertEqual(message.content[0].tool_use_id, "1")
        self.assertEqual(message.content[0].content, [TextBlock(type="text", text="output1")])
        self.assertEqual(message.content[1].content, [TextBlock(type="text", text="output2")])
        self.assertEqual(message.content[2].content, [TextBlock(type="text", text="1")])
        self.assertEqual(
            message.to_json_dict(),
            {
                "role": "user",
                "content": [
                    {"type": "tool_result", "tool_use_id": "1", "content": [{"type": "text", "text": "output1"}]},
                    {"type": "tool_result", "tool_use_id": "2", "content": [{"type": "text", "text": "output2"}]},
                    {"type": "tool_result", "tool_use_id": "3", "content": [{"type": "text", "text": "1"}]},
                ],
            },
        )
