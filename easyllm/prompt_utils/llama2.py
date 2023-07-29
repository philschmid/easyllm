from typing import List

from easyllm.schema.base import ChatMessage

llama2_stop_sequences = ["</s>"]


def build_llama2_prompt(messages: List[ChatMessage]) -> str:
    """
    Uses LLama 2 chat tokens (`[INST]`) to create a prompt, learn more in the [Hugging Face Blog on how to prompt Llama 2](https://huggingface.co/blog/llama2#how-to-prompt-llama-2). If a `Message` with an unsupported `role` is passed, an error will be thrown.
    Args:
        messages (:obj:`List[ChatMessage]`): The messages to use for the completion.
    """

    startPrompt = "<s>[INST] "
    endPrompt = " [/INST]"
    conversation = []

    for index, message in enumerate(messages):
        if message.role == "user":
            conversation.append(message.content.strip())
        elif message.role == "assistant":
            conversation.append(f" [/INST] {message.content}</s><s>[INST] ")
        elif message.role == "function":
            raise ValueError("Llama 2 does not support function calls.")
        elif message.role == "system" and index == 0:
            conversation.append(f"<<SYS>>\n{message.content}\n<</SYS>>\n\n")
        else:
            raise ValueError(f"Invalid message role: {message.role}")

    return startPrompt + "".join(conversation) + endPrompt
