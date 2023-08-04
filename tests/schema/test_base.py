from typing import Any

import pytest

from easyllm.schema.base import ChatMessage, Usage


def test_chat_message() -> None:
    """Test that the ChatMessage schema works as expected."""
    text = "Never gonna give you up. Never gonna let you down."
    role = "user"

    message = ChatMessage(content=text, role=role)

    assert message.content == text
    assert isinstance(message.content, type(text))
    assert message.role == role
    assert isinstance(message.role, type(role))


@pytest.mark.parametrize(
    "role", ["user", "assistant", "function", "system"]
)
def test_all_valid_roles(role: str) -> None:
    """Test that all valid roles are accepted."""
    message = ChatMessage(content="Hello!", role=role)
    assert message.role == role
    assert isinstance(message.role, type(role))


@pytest.mark.parametrize(
    "role",
    ["fellow", "bro", "", 1, 1.0, ["user", "assistant"], {"user": "John Doe"}],
)
def test_all_invalid_roles(role: Any) -> None:
    """Test that all invalid roles are rejected."""
    with pytest.raises(ValueError):
        ChatMessage(content="Hello!", role=role)


@pytest.mark.parametrize(
    "message",
    [1234, ["Hello!"], {"content": "Hello!", "role": "user"}],
)
def test_all_invalid_messages(message: Any) -> None:
    """Test that all invalid messages are rejected."""
    with pytest.raises(ValueError):
        ChatMessage(content=message, role="user")


def test_usage() -> None:
    """Test that the Usage schema works as expected."""
    prompt_tokens = 10
    completion_tokens = 20
    total_tokens = 30

    usage = Usage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )

    assert usage.prompt_tokens == prompt_tokens
    assert isinstance(usage.prompt_tokens, type(prompt_tokens))
    assert usage.completion_tokens == completion_tokens
    assert isinstance(usage.completion_tokens, type(completion_tokens))
    assert usage.total_tokens == total_tokens
    assert isinstance(usage.total_tokens, type(total_tokens))


@pytest.mark.parametrize(
    ["prompt_tokens", "completion_tokens", "total_tokens"],
    [
        ("abc", 10.0, 10),
        (15, "def", 15.0),
        (20, 20.0, "ghi"),
    ],
)
def test_invalid_usage(prompt_tokens, completion_tokens, total_tokens) -> None:
    """Test that invalid Usage inputs are rejected."""
    with pytest.raises(ValueError):
        Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=total_tokens,
        )


@pytest.mark.parametrize(
    ["prompt_tokens", "completion_tokens", "total_tokens"],
    [
        (10, 10, 10),
        ("10", 10, 10),
        (10, "10", 10),
        (10, 10, "10"),
    ],
)
def test_str_to_int_for_usage(
    prompt_tokens, completion_tokens, total_tokens
) -> None:
    """Test that str inputs are converted to int."""
    usage = Usage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
    )

    assert usage.prompt_tokens == 10
    assert isinstance(usage.prompt_tokens, type(10))
    assert usage.completion_tokens == 10
    assert isinstance(usage.completion_tokens, type(10))
    assert usage.total_tokens == 10
    assert isinstance(usage.total_tokens, type(10))
