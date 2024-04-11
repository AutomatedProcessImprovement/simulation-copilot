"""Anthropic package for running complex conversations with Anthropic LLMs.

The package builds on top of the official Anthropic SDK and partially on LangChain.

Typical usage example:

TODO: ...
"""

from enum import Enum


class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Claude3(str, Enum):
    OPUS = "claude-3-opus-20240229"
    SONNET = "claude-3-sonnet-20240229"
    HAIKU = "claude-3-haiku-20240307"
