from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

# Define stop sequences for Vicuna
vicuna_stop_sequences = ["</s>"]


def build_vicuna_prompt(messages: Union[List[Dict[str,str]], str]) -> str:
    """
    Builds a Vicuna prompt for a chat conversation. refrence https://github.com/lm-sys/FastChat/blob/main/docs/vicuna_weights_version.md#prompt-template

    Args:
        messages (Union[List[ChatMessage], str]): The messages to use for the completion.
    Returns:
        str: The Vicuna prompt string.
    """
    VICUNA_EOS_TOKEN = "</s>"
    VICUNA_USER_TOKEN = "USER: "
    VICUNA_ASSISTANT_TOKEN = "ASSISTANT: "

    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{VICUNA_USER_TOKEN}{message.content.strip()}\n")
        elif message.role == "assistant":
            conversation.append(f"{VICUNA_ASSISTANT_TOKEN}{message.content.strip()}{VICUNA_EOS_TOKEN}\n")
        elif message.role == "function":
            raise ValueError("Vicuna does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{message.content.strip()}\n\n")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + VICUNA_ASSISTANT_TOKEN
