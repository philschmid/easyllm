# test_build_open_assistant_prompt.py

from typing import List
import pytest

from easyllm.prompt_utils.open_assistant import build_open_assistant_prompt
from easyllm.schema.base import ChatMessage


def test_build_open_assistant_prompt_single_message():
    message = "Hello!"
    expected_output = f"<|system|></s><|prompter|>{message}</s><|assistant|>"
    result = build_open_assistant_prompt(message)
    assert result == expected_output


def test_build_open_assistant_prompt_multiple_messages():
    messages = [
        ChatMessage(content="You are a chat bot.", role="system"),
        ChatMessage(content="Hello!", role="user"),
    ]
    expected_output = "<|system|>You are a chat bot.</s><|prompter|>Hello!</s><|assistant|>"
    result = build_open_assistant_prompt(messages)
    assert result == expected_output


def test_build_open_assistant_prompt_function_call():
    messages = [
        ChatMessage(content="Hello!", role="user"),
        ChatMessage(content="some_function()", role="function"),
    ]
    with pytest.raises(ValueError, match="Open Assistant does not support function calls."):
        build_open_assistant_prompt(messages)
