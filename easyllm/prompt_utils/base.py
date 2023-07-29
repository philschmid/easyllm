from typing import List

from easyllm.schema.base import ChatMessage


def buildBasePrompt(messages: List[ChatMessage]) -> str:
    conversation = []

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"USER: {message.content.strip()}")
        elif message.role == "assistant":
            conversation.append(f"ASSISTANT: {message.content}")
        elif message.role == "function":
            raise ValueError("Llama 2 does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(message.content)
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return "".join(conversation)
