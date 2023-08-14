from typing import Dict, List, Union

from easyllm.schema.base import ChatMessage

# Define stop sequences for wizardlm
wizardlm_stop_sequences = ["</s>"]


def build_wizardlm_prompt(messages: Union[List[Dict[str,str]], str]) -> str:
    """
    Builds a WizardLM prompt for a chat conversation. refrence https://github.com/nlpxucan/WizardLM/blob/4af9edc59e412a49bba51cd1e8cfac2664e909e5/WizardLM/src/infer_wizardlm13b.py#L79

    Args:
        messages (Union[List[ChatMessage], str]): The messages to use for the completion.
    Returns:
        str: The WizardLM prompt string.
    """
    WIZARDLM_USER_TOKEN = "USER: "
    WIZARDLM_ASSISTANT_TOKEN = "ASSISTANT: "

    conversation = []

    if isinstance(messages, str):
        messages = [ChatMessage(content="", role="system"), ChatMessage(content=messages, role="user")]
    else:
        messages = [ChatMessage(**message) for message in messages]

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(f"{WIZARDLM_USER_TOKEN}{message.content.strip()}")
        elif message.role == "assistant":
            conversation.append(f"{WIZARDLM_ASSISTANT_TOKEN}{message.content.strip()}")
        elif message.role == "function":
            raise ValueError("WizardLM does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"{message.content.strip()}")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return " ".join(conversation).lstrip() + " " + WIZARDLM_ASSISTANT_TOKEN
