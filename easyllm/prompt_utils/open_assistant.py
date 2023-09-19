from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

open_assistant_stop_sequences = ["</s>"]


def build_open_assistant_prompt(messages: Union[List[Dict[str, str]], str], EOS_TOKEN="<|end|>") -> str:
    """
    Uses Open Assistant ChatML template used to in Models. Uses <|prompter|>, </s>, <|system|>, and <|assistant> tokens. If a Message with an unsupported role is passed, an error will be thrown.
    <|system|>system message</s><|prompter|>user prompt</s><|assistant|>
    Args:
        messages (:obj:`List[ChatMessage]`): The messages to use for the completion.
    """

    SYSTEM_TOKEN = "<|system|>"
    USER_TOKEN = "<|prompter|>"
    ASSISTANT_TOKEN = "<|assistant|>"
    EOS_TOKEN = "</s>"
    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        if isinstance(messages[0], dict):
            messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{USER_TOKEN}{message.content.strip()}{EOS_TOKEN}")
        elif message.role == "assistant":
            conversation.append(f"{ASSISTANT_TOKEN}{message.content.strip()}{EOS_TOKEN}")
        elif message.role == "function":
            raise ValueError("Open Assistant does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{SYSTEM_TOKEN}{message.content.strip()}{EOS_TOKEN}")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + ASSISTANT_TOKEN
