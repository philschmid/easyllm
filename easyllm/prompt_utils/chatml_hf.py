from typing import List, Union

from easyllm.schema.base import ChatMessage

chatml_falcon_stop_sequences = ["<|endoftext|>"]


def build_chatml_falcon_prompt(messages: Union[List[ChatMessage], str]) -> str:
    EOS_TOKEN = "<|endoftext|>"
    return build_chatml_hf_prompt(messages, EOS_TOKEN)


chatml_starchat_stop_sequences = ["<|end|>"]


def build_chatml_starchat_prompt(messages: Union[List[ChatMessage], str]) -> str:
    EOS_TOKEN = "<|end|>"
    return build_chatml_hf_prompt(messages, EOS_TOKEN)


def build_chatml_hf_prompt(messages: Union[List[ChatMessage], str], EOS_TOKEN="<|end|>") -> str:
    """
    Uses HuggingFaceH4 ChatML template used to in Models like, StarChat or Falcon. Uses <|user|>, <|end|>, <|system|>, and <|assistant> tokens. If a Message with an unsupported role is passed, an error will be thrown.
    <|system|>\nYou are a chat bot.<|end|>\n<|user|>\nHello!<|end|>\n<|assistant|>\nHi there!<|end|>\n<|assistant|>
    Args:
        messages (:obj:`List[ChatMessage]`): The messages to use for the completion.
    """

    SYSTEM_TOKEN = "<|system|>"
    USER_TOKEN = "<|user|>"
    ASSISTANT_TOKEN = "<|assistant|>"
    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{USER_TOKEN}\n{message.content.strip()}{EOS_TOKEN}\n")
        elif message.role == "assistant":
            conversation.append(f"{ASSISTANT_TOKEN}\n{message.content.strip()}{EOS_TOKEN}\n")
        elif message.role == "function":
            raise ValueError("HF ChatML does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{SYSTEM_TOKEN}\n{message.content.strip()}{EOS_TOKEN}\n")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation) + ASSISTANT_TOKEN
