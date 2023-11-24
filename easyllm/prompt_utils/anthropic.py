from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

# Define stop sequences for anthropic
anthropic_stop_sequences = ["\n\nUser:", "User:"]


def build_anthropic_prompt(messages: Union[List[Dict[str, str]], str, List[ChatMessage]]) -> str:
    """
    Builds a anthropic prompt for a chat conversation. refrence https://huggingface.co/blog/anthropic-180b#prompt-format

    Args:
        messages (Union[List[ChatMessage], str]): The messages to use for the completion.
    Returns:
        str: The anthropic prompt string.
    """
    ANTHROPIC_USER_TOKEN = "\n\nHuman:"
    ANTHROPIC_ASSISTANT_TOKEN = "\n\nAssistant:"

    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        if isinstance(messages[0], dict):
            messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{ANTHROPIC_USER_TOKEN} {message.content.strip()}")
        elif message.role == "assistant":
            conversation.append(f"{ANTHROPIC_ASSISTANT_TOKEN} {message.content.strip()}")
        elif message.role == "function":
            raise ValueError("anthropic does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(message.content)
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + ANTHROPIC_ASSISTANT_TOKEN + " "
