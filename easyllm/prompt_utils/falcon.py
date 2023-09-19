from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

# Define stop sequences for falcon
falcon_stop_sequences = ["\nUser:", "<|endoftext|>", " User:", "###"]


def build_falcon_prompt(messages: Union[List[Dict[str, str]], str, List[ChatMessage]]) -> str:
    """
    Builds a falcon prompt for a chat conversation. refrence https://huggingface.co/blog/falcon-180b#prompt-format

    Args:
        messages (Union[List[ChatMessage], str]): The messages to use for the completion.
    Returns:
        str: The falcon prompt string.
    """
    FALCON_SYSTEM_TOKEN = "System: "
    FALCON_USER_TOKEN = "User: "
    FALCON_ASSISTANT_TOKEN = "Falcon: "

    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        if isinstance(messages[0], dict):
            messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{FALCON_USER_TOKEN}{message.content.strip()}\n")
        elif message.role == "assistant":
            conversation.append(f"{FALCON_ASSISTANT_TOKEN}{message.content.strip()}\n")
        elif message.role == "function":
            raise ValueError("falcon does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{FALCON_SYSTEM_TOKEN}{message.content}\n")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + FALCON_ASSISTANT_TOKEN
