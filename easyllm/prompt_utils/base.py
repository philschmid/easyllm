from typing import List, Union

from easyllm.prompt_utils import PROMPT_MAPPING
from easyllm.schema.base import ChatMessage
from easyllm.utils import setup_logger

logger = setup_logger()


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


def build_prompt(messages: List[ChatMessage], builder: Union[str, callable]) -> str:
    """
    Tries to find the prompt builder in the PROMPT_MAPPING and returns a formatted prompt.
    """
    if isinstance(builder, str):
        prompt_builder = PROMPT_MAPPING.get(builder, None)
        if prompt_builder is None:
            raise ValueError(
                f"Prompt builder {builder} not found. Are you sure you spelled it correctly? \
Available prompt builders are: {PROMPT_MAPPING.keys()}. \
You can open an issue or PR to add more prompt builders at https://github.com/philschmid/easyllm"
            )
        prompt = prompt_builder(messages)
    else:
        prompt = builder(messages)

    logger.debug(f"Prompt sent to model will be:\n{prompt}")
    return prompt
