# test_build_stablebeluga_prompt.py

from typing import List
import pytest

from easyllm.prompt_utils.stablebeluga import build_stablebeluga_prompt
from easyllm.schema.base import ChatMessage


def test_build_stablebeluga_prompt_single_message():
    message = "Hello!"
    expected_output = f"### System:\n\n\n### User:\n{message}\n\n### Assistant:"
    result = build_stablebeluga_prompt(message)
    assert result == expected_output


def test_build_stablebeluga_prompt_multiple_messages():
    messages = [
        ChatMessage(content="You are a chat bot.", role="system"),
        ChatMessage(content="Hello!", role="user"),
    ]
    expected_output = "### System:\nYou are a chat bot.\n\n### User:\nHello!\n\n### Assistant:"
    result = build_stablebeluga_prompt(messages)
    assert result == expected_output


def test_build_stablebeluga_prompt_function_call():
    messages = [
        ChatMessage(content="Hello!", role="user"),
        ChatMessage(content="some_function()", role="function"),
    ]
    with pytest.raises(ValueError, match="stablebeluga does not support function calls."):
        build_stablebeluga_prompt(messages)
