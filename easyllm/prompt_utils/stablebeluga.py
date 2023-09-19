from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

# Define stop sequences for stablebeluga
stablebeluga_stop_sequences = ["</s>"]


def build_stablebeluga_prompt(messages: Union[List[Dict[str, str]], str]) -> str:
    """
    Builds a stablebeluga prompt for a chat conversation. refrence https://huggingface.co/stabilityai/StableBeluga2 or

    Args:
        messages (Union[List[ChatMessage], str]): The messages to use for the completion.
    Returns:
        str: The stablebeluga prompt string.
    """
    SYSTEM_TOKEN = "### System:"
    USER_TOKEN = "### User:"
    ASSISTANT_TOKEN = "### Assistant:"

    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        if isinstance(messages[0], dict):
            messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{USER_TOKEN}\n{message.content.strip()}\n\n")
        elif message.role == "assistant":
            conversation.append(f"{ASSISTANT_TOKEN}\n{message.content.strip()}\n\n")
        elif message.role == "function":
            raise ValueError("stablebeluga does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{SYSTEM_TOKEN}\n{message.content.strip()}\n\n")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + ASSISTANT_TOKEN
