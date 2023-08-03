# test_build_wizardlm_prompt.py

from typing import List
import pytest

from easyllm.prompt_utils.wizardlm import build_wizardlm_prompt
from easyllm.schema.base import ChatMessage


def test_build_wizardlm_prompt_single_message():
    message = "Hello!"
    expected_output = f"USER: {message} ASSISTANT: "
    result = build_wizardlm_prompt(message)
    assert result == expected_output


def test_build_wizardlm_prompt_multiple_messages():
    messages = [
        ChatMessage(content="You are a chat bot.", role="system"),
        ChatMessage(content="Hello!", role="user"),
    ]
    expected_output = "You are a chat bot. USER: Hello! ASSISTANT: "
    result = build_wizardlm_prompt(messages)
    assert result == expected_output


def test_build_wizardlm_prompt_function_call():
    messages = [
        ChatMessage(content="Hello!", role="user"),
        ChatMessage(content="some_function()", role="function"),
    ]
    with pytest.raises(ValueError, match="WizardLM does not support function calls."):
        build_wizardlm_prompt(messages)
