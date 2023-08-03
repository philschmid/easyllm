import pytest

from easyllm.prompt_utils.llama2 import build_llama2_prompt
from easyllm.schema.base import ChatMessage


def test_build_llama2_prompt_single_message():
    message = "Hello!"
    expected_output = f"<s>[INST] {message} [/INST]"
    result = build_llama2_prompt(message)
    assert result == expected_output


def test_build_llama2_prompt_multiple_messages():
    messages = [
        ChatMessage(content="You are a chat bot.", role="system"),
        ChatMessage(content="Hello!", role="user"),
    ]
    expected_output = "<s>[INST] <<SYS>>\nYou are a chat bot.\n<</SYS>>\n\nHello! [/INST]"
    result = build_llama2_prompt(messages)
    assert result == expected_output


def test_build_llama2_prompt_function_call():
    messages = [
        ChatMessage(content="Hello!", role="user"),
        ChatMessage(content="some_function()", role="function"),
    ]
    with pytest.raises(ValueError, match="Llama 2 does not support function calls."):
        build_llama2_prompt(messages)
