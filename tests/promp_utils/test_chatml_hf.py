# test_build_chatml_hf_prompt.py

from typing import List
import pytest

from easyllm.prompt_utils.chatml_hf import build_chatml_hf_prompt
from easyllm.schema.base import ChatMessage


def test_build_chatml_hf_prompt_single_message():
    message = "Hello!"
    expected_output = f"<|system|>\n<|end|>\n<|user|>\n{message}<|end|>\n<|assistant|>"
    result = build_chatml_hf_prompt(message)
    assert result == expected_output


def test_build_chatml_hf_prompt_multiple_messages():
    messages = [
        ChatMessage(content="You are a chat bot.", role="system"),
        ChatMessage(content="Hello!", role="user"),
    ]
    expected_output = "<|system|>\nYou are a chat bot.<|end|>\n<|user|>\nHello!<|end|>\n<|assistant|>"
    result = build_chatml_hf_prompt(messages)
    assert result == expected_output


def test_build_chatml_hf_prompt_function_call():
    messages = [
        ChatMessage(content="Hello!", role="user"),
        ChatMessage(content="some_function()", role="function"),
    ]
    with pytest.raises(ValueError, match="HF ChatML does not support function calls."):
        build_chatml_hf_prompt(messages)
